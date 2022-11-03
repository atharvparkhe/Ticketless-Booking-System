import threading, random, uuid
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.core.cache import cache

context = {}


class send_otp_to_seller(threading.Thread):
    def __init__(self, otp):
        self.otp = otp
        threading.Thread.__init__(self)
    def run(self):
        try:
            send_mail("OTP" , str(self.otp) ,settings.EMAIL_HOST_USER ,[settings.SELLER_EMAIL])
        except Exception as e:
            print(e)


class send_login_otp(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        try:
            otp = random.randint(100001, 999999)
            cache.set(otp, self.email, 350)
            print(otp)
            subject = "OTP to login into your account"
            message = f"The OTP to log in into your email is {otp} \nIts valid only for 2 mins."
            email_from = settings.EMAIL_HOST_USER
            send_mail(subject , message ,email_from ,[self.email])
        except Exception as e:
            print(e)


class send_forgot_link(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        try:
            otp = random.randint(100001, 999999)
            cache.set(otp, self.email, timeout=350)
            context["otp"] = otp
            html_template = 'forgot.html'
            html_message = render_to_string(html_template, context)
            subject = 'OTP to Verify your Account.'
            email_from = settings.EMAIL_HOST_USER
            msg = EmailMessage(subject, html_message, email_from, [self.email])
            msg.content_subtype = 'html'
            msg.send()
        except Exception as e:
                print(e)


class send_special_email(threading.Thread):
    def __init__(self, sub, body, email_list):
        self.sub = sub
        self.body = body
        self.email_list = email_list
        threading.Thread.__init__(self)
    def run(self):
        try:
            subject = self.sub
            message = self.body
            email_from = settings.EMAIL_HOST_USER
            send_mail(subject , message ,email_from ,self.email_list)
        except Exception as e:
            print(e)