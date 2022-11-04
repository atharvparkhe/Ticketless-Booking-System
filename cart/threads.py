import threading, pandas, qrcode
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .utils import *

from PIL import Image, ImageDraw, ImageFont

context = {}


class send_tickets(threading.Thread):
    def __init__(self, cart):
        self.cart = cart
        threading.Thread.__init__(self)
    def run(self):
        try:
            html_template = 'tickets.html'
            html_message = render_to_string(html_template, context)
            subject = 'Your Tickets.'
            email_from = settings.EMAIL_HOST_USER
            msg = EmailMessage(subject, html_message, email_from, [self.cart.owner.email])
            msg.content_subtype = 'html'

            img = Image.open("ticket.jpeg")
            font = ImageFont.truetype("font.ttf", 30)
            draw = ImageDraw.Draw(img)

            for obj in self.cart.related_cart.all():

                qr = qrcode.make(str(self.cart.id))
                file_name = "data/QR/" + str(self.cart.id) + ".jpeg"
                qr.save(file_name)
                obj.qr_img = file_name
                draw.text(xy=(150, 40), text=str(obj.item.name), fill=(0,0,0), font=font)
                draw.text(xy=(220, 83), text=str(obj.owner.f_name) + "  " + str(obj.owner.l_name), fill=(0,0,0), font=font)
                draw.text(xy=(280, 130), text=str(obj.quantity), fill=(0,0,0), font=font)
                draw.text(xy=(135, 170), text=str(obj.date), fill=(0,0,0), font=font)
                draw.text(xy=(135, 215), text=str(obj.time_slot.start_time) + " - " + str(obj.time_slot.end_time), fill=(0,0,0), font=font)
                path = "data/temp/" + str(obj.id) + ".jpeg"
                img.save(path)
                im1 = Image.open(file_name)
                im2 = Image.open(path)
                ticket = im2.copy()
                ticket.paste(im1, (700, 25))
                final_path = "data/Tickets/" + str(self.cart.id) + ".jpeg"
                ticket.save(final_path)
                obj.ticket = final_path
                obj.save()
                msg.attach_file(path)

            msg.send()
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
