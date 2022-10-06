from flask import redirect, render_template, url_for
from app.forms import UpdateResourceForm
from app.utils import _fetch_subject_list, _fetch_resource_df, _update_form_according_to_resource, _update_resource_according_to_form, _insert_resource_according_to_form, _fetch_course, _update_resource_discord_link
import discord
import asyncio
import os

class DiscordClientForCreatingThread(discord.Client):
    channel_id = None
    uploaded_resources = None
    thread_link = None

    def __init__(self, channel_id, uploaded_resources):
        self.channel_id = channel_id
        self.uploaded_resources = uploaded_resources
        intents = discord.Intents.default()
        intents.guild_messages = True
        intents.guilds = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.do = False

    async def on_ready(self):
        channel = self.get_channel(self.channel_id)
        for i in self.uploaded_resources:
            msg = await channel.send("חומר לימוד חדש")
            thread_name = i[1]
            if i[2]:
                thread_name += ' - ' + i[2]
            thread = await msg.create_thread(name=thread_name.strip('?'))
            await msg.delete()
            await thread.send("<https://studybuddy.co.il/resource/{0}>".format(i[0]))
            _update_resource_discord_link(i[0], thread.jump_url)
        await self.close()

async def create_discord_threads(channel_id, uploaded_resources):
    if os.environ.get("DISCORD_TOKEN"):
        client = DiscordClientForCreatingThread(channel_id=channel_id, uploaded_resources=uploaded_resources)
        await client.start(os.environ.get("DISCORD_TOKEN"))

def _update_resource(course_id, is_existing_resource, resource_id=None):
    form = UpdateResourceForm()

    form.subject.choices = _fetch_subject_list()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        if is_existing_resource:
            resource_df = _fetch_resource_df(resource_id)
            resource = resource_df.iloc[0]
            form = _update_form_according_to_resource(form, resource)

        return render_template('updateresource.html', form=form, is_existing_resource=is_existing_resource)

    # Form was submitted with valid input
    if form.validate_on_submit():
        if is_existing_resource:
            resource_df = _fetch_resource_df(resource_id)
            resource = resource_df.iloc[0]
            _update_resource_according_to_form(resource, form)

        else:
            course = _fetch_course(course_id)
            uploaded_resources = _insert_resource_according_to_form(form, course_id)

            channel_id = int(course.discord_channel_id)
            asyncio.run(create_discord_threads(channel_id, uploaded_resources))

        return redirect(url_for('course', course_id=course_id))
