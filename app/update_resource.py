from flask import redirect, render_template, url_for
from app.forms import UpdateResourceForm
from app.utils import _fetch_subject_list, _fetch_resource_df, _update_form_according_to_resource, _update_resource_according_to_form, _insert_resource_according_to_form, _fetch_course, _update_resource_discord_link
import discord
import asyncio
import os
from threading import Thread


class DiscordClientForCreatingThread(discord.Client):
    course = None
    guild = None
    uploaded_resources = None
    thread_link = None

    def __init__(self, course, uploaded_resources):
        self.course = course
        self.uploaded_resources = uploaded_resources
        intents = discord.Intents.default()
        intents.guild_messages = True
        intents.guilds = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.do = False

    async def on_ready(self):
        try:

            self.guild = await self.fetch_guild(int(self.course[0]))
            for resource in self.uploaded_resources:
                channel = None
                topic = "<https://studybuddy.co.il/{0}/{1}/resource/{2}>".format(self.course[1],
                                                                                 self.course[2], resource[0])

                if resource[4]:
                    channel = self.guild.get_channel(int(resource[4].split('/')[5]))

                if channel:
                    if resource[2] == 'lecture':
                        if channel.name != resource[1]:
                            await channel.edit(name=resource[1], topic=topic)
                    if resource[2].startswith('exercise') or resource[2].startswith('exam'):
                        if channel.name != resource[1]:
                            await channel.edit(name=resource[3] + ' ' + resource[1], topic=topic)
                    if resource[2] == 'other':
                        await channel.edit(name="[אחר] " + resource[1], topic=topic)
                        _update_resource_discord_link(resource[0], None)

                else:
                    if resource[2] == 'lecture':
                        channel = await self.guild.create_text_channel(resource[1], topic=topic)
                    if resource[2].startswith('exercise'):
                        channel = await self.guild.create_text_channel(resource[3] + ' ' + resource[1], topic=topic)
                    if resource[2].startswith('exam'):
                        channel = await self.guild.create_text_channel(resource[3] + ' ' + resource[1], topic=topic)

                    if channel:
                        _update_resource_discord_link(resource[0], channel.jump_url)
        except Exception as e:
            print(e)
        finally:
            await self.close()


async def async_update_discord_threads(course, uploaded_resources):
    if os.environ.get("DISCORD_TOKEN"):
        client = DiscordClientForCreatingThread(course=course, uploaded_resources=uploaded_resources)
        await client.start(os.environ.get("DISCORD_TOKEN"))


def update_discord_threads(course, uploaded_resources):
    asyncio.run(async_update_discord_threads(course, uploaded_resources))


def _update_resource(course_id, institute, institute_course_id, is_existing_resource, resource_id=None):
    form = UpdateResourceForm()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        if is_existing_resource:
            resource_df = _fetch_resource_df(resource_id)
            resource = resource_df.iloc[0]
            form = _update_form_according_to_resource(form, resource)

        return render_template('updateresource.html', form=form, is_existing_resource=is_existing_resource, course_subjects=_fetch_subject_list(course_id))

    # Form was submitted with valid input
    if form.validate_on_submit():
        course = _fetch_course(course_id)
        if is_existing_resource:
            resource_df = _fetch_resource_df(resource_id)
            resource = resource_df.iloc[0]
            updated_resources = _update_resource_according_to_form(resource, form)

        else:
            updated_resources = _insert_resource_according_to_form(form, course_id)

        thread = Thread(target=update_discord_threads, args=((course.discord_channel_id,
                        course.course_institute_english, course.course_institute_id), updated_resources))
        thread.start()

        if form.type.data == 'lecture':
            return redirect(url_for('course', institute=institute, institute_course_id=institute_course_id))
        if form.type.data.startswith('exercise'):
            return redirect(url_for('exercises', institute=institute, institute_course_id=institute_course_id))
        if form.type.data.startswith('exam'):
            return redirect(url_for('exams', institute=institute, institute_course_id=institute_course_id))
        if form.type.data == 'other':
            return redirect(url_for('archive', institute=institute, institute_course_id=institute_course_id))
        thread.join()
