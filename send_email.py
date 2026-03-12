import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

user   = os.environ["MAIL_USER"]
passwd = os.environ["MAIL_PASS"]
status = os.environ.get("STATUS", "unknown")

try:
    output = open("agent_output.txt").read()
except:
    output = "Žiadny výstup"

date    = datetime.now().strftime("%d.%m.%Y %H:%M")
emoji   = "✅" if status == "success" else "❌"
subject = f"{emoji} WeatherAgent {date} — {status.upper()}"

body = f"""WeatherAgent denný beh

Dátum:  {date}
Status: {emoji} {status.upper()}

Výstup:
{output}

GitHub: https://github.com/slavo1976/AgentWeather/blob/main/WeatherHistory.xlsx
"""

msg = MIMEMultipart()
msg["From"]    = user
msg["To"]      = user
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain", "utf-8"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(user, passwd)
    s.send_message(msg)
    print("Email odoslaný.")
