from app import app
from apscheduler.schedulers.background import BackgroundScheduler

def scheduled_task():
    with app.app_context():
        print("This is a scheduled task.")

scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_task, trigger="interval", minutes=60)
scheduler.start()