import threading, pandas, qrcode
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .utils import *

from PIL import Image, ImageDraw, ImageFont

img = Image.open("ticket.jpeg")
font = ImageFont.truetype("font.ttf", 30)
draw = ImageDraw.Draw(img)

context = {}

# im1 = Image.open(file_name)
# im2 = Image.open(path)

# ticket = im2.copy()
# ticket.paste(im1, (700, 25))
# ticket.save("main.jpeg")

class send_tickets(threading.Thread):
    def __init__(self, cart):
        self.cart = cart
        threading.Thread.__init__(self)
    def run(self):
        try:
            qr = qrcode.make("hello")
            file_name = "data/QR/" + str(self.cart.id) + ".jpeg"
            qr.save(file_name)
            # draw.text(xy=(150, 40), text="Old Goa Church", fill=(0,0,0), font=font)
            # draw.text(xy=(220, 83), text="Atharva Parkhe", fill=(0,0,0), font=font)
            # draw.text(xy=(280, 130), text="3", fill=(0,0,0), font=font)
            # draw.text(xy=(135, 170), text="2022-11-03", fill=(0,0,0), font=font)
            # draw.text(xy=(135, 215), text="09:00:00 - 10:00:00", fill=(0,0,0), font=font)
            # path = "tickets/temp.jpeg"
            # img.save(path)
        except Exception as e:
            print(e)


class generate_invoice(threading.Thread):
    def __init__(self, order):
        self.order = order
        threading.Thread.__init__(self)
    def run(self):
        try:
            html_template = 'order.html'
            html_message = render_to_string(html_template, context)
            subject = 'Your Order Summary.'
            email_from = settings.EMAIL_HOST_USER
            msg = EmailMessage(subject, html_message, email_from, [self.order.owner.email])
            msg.content_subtype = 'html'

            params = {
                "cart_obj" : self.order,
                "cart_items" : self.order.related_cart.all()
            }

            file_path, status = save_invoice(params)

            if status:
                path = "data/invoice/" + file_path + ".pdf"
                self.order.invoice = path
                self.order.save()
                msg.attach_file(path)
                msg.send()
            else : pass
        except Exception as e:
            print(e)


class take_backup(threading.Thread):
    def __init__(self, obj_list):
        self.obj_list = obj_list
        threading.Thread.__init__(self)
    def run(self):
        try:
            data = []
            for obj in self.obj_list:
                l1 = [obj.owner.name, obj.total_price, obj.tax, obj.total_amt, obj.coupon_applied, obj.order_id, obj.payment_id, obj.payment_signature]
                data.append(l1)
            data = pandas.DataFrame(data, columns= ['Customer', 'Price', 'Tax', 'Total', 'Coupon Applied', 'Order ID', 'Payment ID', 'Payment Signature'] )
            file_name = "data/backup/output.xlsx"
            data.to_excel(file_name)
            sub = "Order Details Backup"
            body = "Order Details Backup file"
            msg = EmailMessage(sub, body, settings.EMAIL_HOST_USER, [settings.SELLER_EMAIL])
            msg.content_subtype = "html"
            msg.attach_file(str(file_name))
            msg.send()
        except Exception as e:
            print(e)
