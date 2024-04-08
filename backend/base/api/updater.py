from apscheduler.schedulers.background import BackgroundScheduler
from base.api.views import check_kpi_actulas_pending, check_monthly_actuals_remainder, session_active_check
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# check_kpi_actulas_pending()
# check_monthly_actuals_remainder()
def jobs():
    print("Jobs scheduler Running")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_kpi_actulas_pending, 'interval', hours=12) 
    scheduler.add_job(session_active_check, 'interval', minutes=15)
    scheduler.start()