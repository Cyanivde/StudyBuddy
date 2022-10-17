
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

import app.discordbots as discordbots
from threading import Thread
thread = Thread(target=discordbots.create_discord_bot_for_moving_channels, args=(app,db))
thread.start()


# trunk-ignore(flake8/F401)
# trunk-ignore(flake8/E402)
from app import routes, models


