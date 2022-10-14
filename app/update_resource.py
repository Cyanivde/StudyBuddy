from flask import redirect, render_template, url_for
from app.forms import UpdateResourceForm
from app.utils import _fetch_subject_list, _fetch_resource_df, _update_form_according_to_resource, _update_resource_according_to_form, _insert_resource_according_to_form, _fetch_course, _update_resource_discord_link
import discord
import asyncio
import os


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

        self.guild = self.get_guild(int(self.course.discord_channel_id))

        lectures_category = [cat for cat in self.guild.categories if cat.name == 'שיעורים'][0]
        exercises_category = [cat for cat in self.guild.categories if cat.name == 'תרגילי בית'][0]
        exams_category = [cat for cat in self.guild.categories if cat.name == 'מבחנים'][0]

        for resource in self.uploaded_resources:
            channel = None

            if resource.comments:
                print(resource.comments)
                channel = await self.guild.fetch_channel(int(resource.comments.split('/')[5]))

            if channel:
                if resource.type == 'lecture':
                    if channel.name != resource.display_name:
                        await channel.edit(name=resource.display_name)
                if resource.type.startswith('exercise') or resource.type.startswith('exam'):
                    if channel.name != resource.display_name:
                        await channel.edit(name=resource.semester + ' ' + resource.display_name)
                if resource.type == 'other':
                    await channel.edit(name="[אחר] " + resource.display_name)
                    _update_resource_discord_link(resource.resource_id, None)

            else:
                if resource.type == 'lecture':
                    channel = await self.guild.create_text_channel(resource.display_name, category=lectures_category)
                if resource.type.startswith('exercise'):
                    channel = await self.guild.create_text_channel(resource.semester + ' ' + resource.display_name, category=exercises_category)
                if resource.type.startswith('exam'):
                    channel = await self.guild.create_text_channel(resource.semester + ' ' + resource.display_name, category=exams_category)

                if channel:
                    await channel.edit(topic="<https://studybuddy.co.il/{0}/{1}/resource/{2}>".format(self.course.course_institute_english,
                                                                                                      self.course.course_institute_id, resource.resource_id))
                    _update_resource_discord_link(resource.resource_id, channel.jump_url)

        await self.close()


async def update_discord_threads(course, uploaded_resources):
    if os.environ.get("DISCORD_TOKEN"):

        client = DiscordClientForCreatingThread(course=course, uploaded_resources=uploaded_resources)
        await client.start(os.environ.get("DISCORD_TOKEN"))


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

        asyncio.run(update_discord_threads(course, updated_resources))

        if form.type.data == 'lecture':
            return redirect(url_for('course', institute=institute, institute_course_id=institute_course_id))
        if form.type.data.startswith('exercise'):
            return redirect(url_for('exercises', institute=institute, institute_course_id=institute_course_id))
        if form.type.data.startswith('exam'):
            return redirect(url_for('exams', institute=institute, institute_course_id=institute_course_id))
        if form.type.data == 'other':
            return redirect(url_for('archive', institute=institute, institute_course_id=institute_course_id))
