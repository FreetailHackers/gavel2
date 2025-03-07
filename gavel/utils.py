from gavel import celery
import gavel.settings as settings
import gavel.crowd_bt as crowd_bt
import gavel.constants as constants
from flask import Markup, Response, request, render_template
import markdown
import requests
from functools import wraps
import base64
import os
import csv
import io
import re
import smtplib
import email
import email.mime.multipart
import email.mime.text
import json
import types

import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


def async_action(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return loop.run_until_complete(f(*args, **kwargs))

    return wrapped


def async_future(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.Future(f(*args, **kwargs))

    return wrapped


sendgrid_url = "https://api.sendgrid.com/v3/mail/send"


def gen_secret(length):
    return base64.b32encode(os.urandom(length))[:length].decode("utf8").lower()


def check_auth(username, password):
    return username == "admin" and password == settings.ADMIN_PASSWORD


def authenticate():
    return Response(
        "Access denied.", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def data_to_csv_string(data):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(data)
    return output.getvalue()


def data_from_csv_string(string):
    data_input = io.StringIO(string)
    reader = csv.reader(data_input)
    return list(reader)


def get_paragraphs(message):
    paragraphs = re.split(r"\n\n+", message)
    paragraphs = [i.replace("\n", " ") for i in paragraphs if i]
    return paragraphs


@celery.task(name="utils.send_emails")
def send_emails(emails):
    print("Starting send emails")
    if settings.EMAIL_PROVIDER not in ["smtp", "sendgrid", "mailgun"]:
        raise Exception(
            "[EMAIL ERROR]: Invalid email provider. Please select one of: smtp, sendgrid, mailgun"
        )
    if settings.EMAIL_PROVIDER == "smtp":
        print("Sending smtp emails")
        send_smtp_emails.apply_async(args=[emails])
    else:
        print("y no smtp?")
        exceptions = []
        for e in emails:
            to_address, subject, body = e
            response = {}
            to_adddress = to_address[0:]
            try:
                if settings.EMAIL_PROVIDER == "sendgrid":
                    response = loop.run_until_complete(
                        sendgrid_send_email(to_address, subject, body)
                    )
                elif settings.EMAIL_PROVIDER == "mailgun":
                    response = loop.run_until_complete(
                        mailgun_send_email(to_adddress, subject, body)
                    )
                if not (
                    response.status_code == requests.codes.ok
                    or response.status_code == requests.codes.accepted
                ):
                    # all_errors = [error_obj["message"] for error_obj in response.json()["errors"]]
                    error_msg = to_address
                    exceptions.append(error_msg)

            except Exception as e:
                exceptions.append(e)
        if exceptions:
            raise Exception(
                "Error sending some emails. Please double-check your email authentication settings.",
                exceptions,
            )


@celery.task(name="utils.send_smtp_emails")
def send_smtp_emails(emails):
    """
    Send a batch of emails.

    This function takes a list [(to_address, subject, body)].
    """

    print("Sending smtp emails from", settings.EMAIL_FROM, "...")
    if settings.EMAIL_AUTH_MODE == "tls":
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        print("Using host", settings.EMAIL_HOST, "on port", settings.EMAIL_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()

    elif settings.EMAIL_AUTH_MODE == "ssl":
        print("Why are we on SSL?")
        server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
    elif settings.EMAIL_AUTH_MODE == "none":
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.ehlo()
    else:
        raise ValueError("unsupported auth mode: %s" % settings.EMAIL_AUTH_MODE)

    server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)

    exceptions = []
    for e in emails:
        print("  Attempting to send email:", e)
        try:
            to_address, subject, body = e
            msg = email.mime.multipart.MIMEMultipart()
            msg["From"] = settings.EMAIL_FROM
            msg["To"] = to_address
            recipients = [to_address]
            if settings.EMAIL_CC:
                msg["Cc"] = ", ".join(settings.EMAIL_CC)
                recipients.extend(settings.EMAIL_CC)
            msg["Subject"] = subject
            msg.attach(email.mime.text.MIMEText(body, "plain"))
            print(
                "  Sent; results:",
                server.sendmail(settings.EMAIL_FROM, recipients, msg.as_string()),
            )
        except Exception as e:
            exceptions.append(e)  # XXX is there a cleaner way to handle this?
            print("  Error:", e)

    server.quit()
    if exceptions:
        raise Exception("Error sending some emails: %s" % exceptions)


async def sendgrid_send_email(to_address, subject, body):
    print("EWWW SENDGRID")
    new_dict = {}
    new_dict["personalizations"] = []
    new_dict["personalizations"].append(
        {"to": [{"email": to_address}], "subject": subject}
    )
    new_dict["from"] = {}
    new_dict["from"]["email"] = settings.EMAIL_FROM
    new_dict["subject"] = subject
    new_dict["content"] = []
    new_dict["content"].append({"type": "text/plain", "value": body})
    headers = {
        "authorization": "Bearer " + settings.SENDGRID_API_KEY,
        "content-type": "application/json",
    }
    response = requests.post(sendgrid_url, data=json.dumps(new_dict), headers=headers)
    return response


async def mailgun_send_email(to_address, subject, body):
    print("EWWW MAILGUN")
    api_url = "https://api.mailgun.net/v3/" + settings.MAILGUN_DOMAIN + "/messages"
    mailgun_key = settings.MAILGUN_API_KEY
    response = requests.post(
        api_url,
        auth=("api", mailgun_key),
        data={
            "from": settings.EMAIL_FROM,
            "to": [to_address],
            "subject": subject,
            "text": body,
        },
    )
    return response


def render_markdown(content):
    return Markup(markdown.markdown(content))


def user_error(message):
    return render_template("error.html", message=message), 400


def server_error(message):
    return render_template("error.html", message=message), 500


def send_telemetry(identifier, data):
    if not settings.SEND_STATS:
        return
    try:
        requests.post(
            constants.TELEMETRY_URL,
            json={"identifier": identifier, "data": data},
            timeout=5,
        )
    except Exception:
        pass  # don't want this to break anything else


def cast_row(row):
    """
    Convert workbook sheet cells into integers if they are equal to integer
    values and convert everything to a string.

    The xlrd library seems to import cells as float values if the cell had a
    numeric value, so this method is needed to correct that.
    """
    for i, item in enumerate(row):
        if isinstance(item, (float, int)) and int(item) == item:
            row[i] = str(int(item))
        else:
            row[i] = str(item)
    return row
