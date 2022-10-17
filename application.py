from app import app, db
from app.models import User

import app.discordbots as discordbots
from threading import Thread
thread = Thread(target=discordbots.create_discord_bot_for_moving_channels)
thread.start()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}
