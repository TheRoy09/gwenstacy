from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
scheduler = BackgroundScheduler()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    scheduler.start()
    mail.init_app(app)

    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    # Import routes and tasks
    from app import routes, tasks

    return app

app = create_app()

# Create the database tables if they don't exist yet
with app.app_context():
    db.create_all()