from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from app.models import *
from .serializers import *
from .threads import *
from .models import *

import razorpay, qrcode
from twilio.rest import Client


twilio_client = Client(settings.TWILIO_ACCOUNT_ID, settings.TWILIO_AUTH_TOKEN)

client = razorpay.Client(auth=(settings.RAZORPAY_PUBLIC_KEY, settings.RAZORPAY_PRIVATE_KEY))



@api_view(["POST"])
def book_now(request):
    try:
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated]
        data = request.data
        customer = CustomerModel.objects.get(email=request.user.email)
        serializer = ModifyCartItemsSerializer(data=data)
        if serializer.is_valid():
            if not PlaceModel.objects.filter(id=serializer.data["place_id"]):
                return Response({"message":"Invalid Place ID"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if not TimeSlotModel.objects.filter(id=serializer.data["slot_id"]):
                return Response({"message":"Invalid Time Slot ID"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            place_obj = PlaceModel.objects.get(id=serializer.data["place_id"])
            time_slot_obj = TimeSlotModel.objects.get(id=serializer.data["slot_id"])
            cart_obj, _ = OrderModel.objects.get_or_create(owner=customer, is_paid=False)
            appointment = serializer.data["date"]
            quan = int(serializer.data["quantity"])
            if cart_obj.related_cart.filter(item=place_obj, date=appointment).exists():
                cart_item = OrderItemsModel.objects.get(cart=cart_obj, item=place_obj, appoitment=appointment, time_slot=time_slot_obj)
                cart_item.quantity += quan
                cart_item.save()
            else :
                OrderItemsModel.objects.create(
                    owner=customer,
                    cart=cart_obj,
                    item=place_obj,
                    appoitment=appointment,
                    time_slot=time_slot_obj,
                    quantity=quan
                )
            ser = OrderItemSerializer(cart_obj.related_cart.all(), many=True)
            return Response({"data":ser.data, "message":"Booking done"}, status=status.HTTP_202_ACCEPTED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def apply_coupon(request):
    try:
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated]
        data = request.data
        customer = CustomerModel.objects.get(email=request.user)
        serializer = CouponSerializer(data=data)
        if serializer.is_valid():
            cart_obj = OrderModel.objects.get(owner=customer)
            if not cart_obj:
                return Response({"message":"Cart does not exist"}, status=status.HTTP_403_FORBIDDEN)
            if CouponsModel.objects.filter(coupon_name=serializer.data["coupon_code"]).exists() and cart_obj.coupon_applied == False:
                coupon_obj = CouponsModel.objects.get(coupon_name = serializer.data["coupon_code"])
                cart_obj.total_amt -= cart_obj.total_amt*coupon_obj.coupon_discount_amount
                cart_obj.coupon_applied = True
                cart_obj.save()
                coupon_obj.save()
                return Response({"message":"Coupon Applied"}, status=status.HTTP_202_ACCEPTED)
            return Response({"message":"invalid coupon code"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def checkout(request):
    try:
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated]
        user = CustomerModel.objects.get(email=request.user.email)
        if not OrderModel.objects.filter(owner=user, is_paid=False).exists():
            return Response({"message":"No items exist in cart"}, status=status.HTTP_404_NOT_FOUND)
        cart_obj = OrderModel.objects.get(owner=user, is_paid=False)
        payment = client.order.create({
            'amount' :  cart_obj.total_amt * 100,
            'currency' : 'INR',
            'payment_capture' : 1
        })
        if cart_obj.razorpay_order_id == None:
            cart_obj.razorpay_order_id = payment["id"]
            cart_obj.save()
        serializer = OrderSerializer(cart_obj)
        return Response({"cart":serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def resultPage(request):
    try:
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated]
        data = request.data
        user = CustomerModel.objects.get(email=request.user.email)
        cart_obj = OrderModel.objects.get(owner=user, is_paid=False)
        serializer = PaymentCredentials(data=data)
        if serializer.is_valid():
            payment_credentials = {
                "razorpay_order_id" : cart_obj.razorpay_order_id,
                "razorpay_payment_id" : serializer.data["razorpay_payment_id"],
                "razorpay_signature" : serializer.data["razorpay_signature"]
            }
            check = client.utility.verify_payment_signature(payment_credentials)
            if check:
                return Response({"message":"Payment Failed"}, status=status.HTTP_403_FORBIDDEN)
            cart_obj.payment_id = payment_credentials["razorpay_payment_id"]
            cart_obj.payment_signature = payment_credentials["razorpay_signature"]
            cart_obj.is_paid = True
            thread_obj = generate_invoice(cart_obj)
            thread_obj.start()
            thread_obj_2 = send_tickets(cart_obj)
            thread_obj_2.start()
            cart_obj.save()
            # s = f"New Order\nCustomer Name: {cart_obj.owner.f_name} {cart_obj.owner.l_name}\nCustomer Email ID: {cart_obj.owner.email}\nCustomer Phone No: {cart_obj.owner.phone}\n\n"
            # for cart_item in cart_obj.related_cart.all():
            #     s += f"Activity: {cart_item.item.name}\nDate: {cart_item.appoitment}\nSeats: {cart_item.quantity}\nTimm Slot: {cart_item.time_slot.slot_start_time}-{cart_item.time_slot.slot_end_time}\n"
            # twilio_client.messages.create(
            #     from_ = 'whatsapp:+14155238886',
            #     body = s,
            #     to = f"whatsapp:+918007609672"
            # )
            return Response({"message":"Payment Successfull"}, status=status.HTTP_200_OK)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["POST"])
def scan_ticket(request):
    try:
        ser = ScanQRSerializer(data=request.data)
        if ser.is_valid():
            decoded_string = ser.data["decoded_string"]
            return Response({"is_success":False}, status=status.HTTP_200_OK)
        return Response({"error":ser.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# qr = qrcode.make(ser.data["text"])
# file_name = "data/download/" + str(uuid.uuid4()) + ".jpeg"
# qr.save(file_name)