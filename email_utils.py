from constants import SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENTS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from constants import HOUSE_MEETING_LINK, HOUSE_PROJECTS_LINK

def build_email_body(grouped_tasks, next_meeting_url=None):
    body = f"""
    <h2>🏡 House Meeting Prep</h2>
    <p>Hi Johanni & Jimmy!<br>
    Here's your friendly check-in for our upcoming House Meeting. Let's celebrate what's done and get motivated for what's next! 🎉</p>
    <p><b>House Meeting page:</b> <a href=\"{HOUSE_MEETING_LINK}\">Click here</a></p>
    <p><b>House Projects database:</b> <a href=\"{HOUSE_PROJECTS_LINK}\">Click here</a></p>
    <hr>
    """
    if next_meeting_url:
        body += f'<p><b>Next House Meeting Page:</b> <a href="{next_meeting_url}">Open next meeting</a></p>'
    for owner in ["Johanni", "Jimmy"]:
        body += f"<h3>{owner}'s Tasks:</h3><ul>"
        if grouped_tasks[owner]:
            for task in grouped_tasks[owner]:
                body += f"<li>{task['formatted']}</li>" if 'formatted' in task else f"<li>{task}</li>"
        else:
            body += "<li>No tasks assigned this meeting! 🎉</li>"
        body += "</ul>"
    if grouped_tasks["Other"]:
        body += "<h3>Together:</h3><ul>"
        for task in grouped_tasks["Other"]:
            body += f"<li>{task['formatted']}</li>" if 'formatted' in task else f"<li>{task}</li>"
        body += "</ul>"
    body += "<hr><p>Let's keep up the great work! 💪</p>"
    return body

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ", ".join(RECIPIENTS)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECIPIENTS, msg.as_string()) 