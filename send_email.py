import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

user   = os.environ["MAIL_USER"]
passwd = os.environ["MAIL_PASS"]
status = os.environ.get("STATUS", "unknown")
token  = os.environ.get("GITHUB_TOKEN", "")

try:
    output = open("agent_output.txt").read()
except:
    output = "Žiadny výstup"

date  = datetime.now().strftime("%d.%m.%Y %H:%M")
emoji = "✅" if status == "success" else "❌"

subject = f"{emoji} WeatherAgent {date} — {status.upper()}"

body = f"""WeatherAgent denný beh

Dátum:  {date}
Status: {emoji} {status.upper()}

Výstup:
{output}

GitHub: https://raw.githubusercontent.com/slavo1976/AgentWeather/main/WeatherHistory.xlsx
"""

msg = MIMEMultipart()
msg["From"]    = user
msg["To"]      = user
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain", "utf-8"))

# Stiahni Excel z GitHub a prilož k emailu
excel_url = "https://raw.githubusercontent.com/slavo1976/AgentWeather/main/WeatherHistory.xlsx"
headers   = {"Authorization": f"token {token}"} if token else {}

try:
    resp = requests.get(excel_url, headers=headers, timeout=20)
    resp.raise_for_status()

    attachment = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    attachment.set_payload(resp.content)
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename="WeatherHistory.xlsx")
    msg.attach(attachment)
    print(f"Excel priložený ({len(resp.content) // 1024} KB).")
except Exception as e:
    print(f"Excel sa nepodarilo priložiť: {e}")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(user, passwd)
    s.send_message(msg)
    print("Email odoslaný.")
