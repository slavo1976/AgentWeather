import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from urllib.parse import quote
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

raw_url    = "https://raw.githubusercontent.com/slavo1976/AgentWeather/main/WeatherHistory.xlsx"
github_url = "https://github.com/slavo1976/AgentWeather/blob/main/WeatherHistory.xlsx"
encoded    = quote(raw_url, safe="")
office_url = f"https://view.officeapps.live.com/op/view.aspx?src={encoded}"

body_plain = f"""WeatherAgent denný beh

Dátum:  {date}
Status: {emoji} {status.upper()}

📥 Stiahnuť Excel:          {raw_url}
📋 Otvoriť v Office Online: {office_url}
🔗 GitHub repozitár:        {github_url}

Výstup:
{output}
"""

body_html = f"""
<html><body style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">

<h2 style="color: {'#2e7d32' if status == 'success' else '#c62828'};">
  {emoji} WeatherAgent — {status.upper()}
</h2>

<p><strong>Dátum:</strong> {date}</p>

<hr style="border: none; border-top: 1px solid #ddd; margin: 16px 0;">

<p><strong>📂 Otvoriť / stiahnuť súbor:</strong></p>

<table cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td style="padding: 6px 8px 6px 0;">
      <a href="{raw_url}"
         style="background:#1565C0; color:#fff; padding:8px 16px; border-radius:6px;
                text-decoration:none; font-size:13px; display:inline-block;">
        📥 Stiahnuť Excel
      </a>
    </td>
    <td style="padding: 6px 8px;">
      <a href="{office_url}"
         style="background:#D83B01; color:#fff; padding:8px 16px; border-radius:6px;
                text-decoration:none; font-size:13px; display:inline-block;">
        📋 Office Online
      </a>
    </td>
    <td style="padding: 6px 0 6px 8px;">
      <a href="{github_url}"
         style="background:#24292e; color:#fff; padding:8px 16px; border-radius:6px;
                text-decoration:none; font-size:13px; display:inline-block;">
        🔗 GitHub
      </a>
    </td>
  </tr>
</table>

<hr style="border: none; border-top: 1px solid #ddd; margin: 16px 0;">

<p><strong>📄 Výstup agenta:</strong></p>
<pre style="background:#f5f5f5; padding:12px; border-radius:6px;
            font-size:12px; color:#444; white-space:pre-wrap;">{output}</pre>

</body></html>
"""

msg = MIMEMultipart("alternative")
msg["From"]    = user
msg["To"]      = user
msg["Subject"] = subject
msg.attach(MIMEText(body_plain, "plain", "utf-8"))
msg.attach(MIMEText(body_html,  "html",  "utf-8"))

# Excel príloha
headers_req = {"Authorization": f"token {token}"} if token else {}
try:
    resp = requests.get(raw_url, headers=headers_req, timeout=20)
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
