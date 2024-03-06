from apscheduler.schedulers.background import BackgroundScheduler
from base.api.views import check_kpi_actulas, session_active_check
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def jobs():
    print("Jobs scheduler Running")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_kpi_actulas, 'interval', hours=2) 
    scheduler.add_job(session_active_check, 'interval', minutes=15)
    scheduler.start()