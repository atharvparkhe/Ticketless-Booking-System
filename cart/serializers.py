from rest_framework import serializers
from .models import *
from rest_framework import serializers
from authentication.serializers import CustomerDetailsSerializer
from app.serializers import MultiPlacesModelSerializer
from .models import *


class ScanQRSerializer(serializers.Serializer):
    place_id = serializers.CharField(required=True)
    decoded_string = serializers.CharField(required=True)


class OrderItemSerializer(serializers.ModelSerializer):
    item = MultiPlacesModelSerializer()
    class Meta:
        model = OrderItemsModel
        fields = ["item", "quantity", "total", "date"]


class OrderSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()
    owner = CustomerDetailsSerializer()
    class Meta:
        model = OrderModel
        exclude = ["created_at", "updated_at", "is_paid", "razorpay_payment_id", "razorpay_signature", "cancellation_request"]
    def get_cart_items(self, obj):
        cart_items = []
        try:
            cart_obj = OrderModel.objects.get(id = obj.id)
            serializer = OrderItemSerializer(cart_obj.related_cart.all(), many=True)
            cart_items = serializer.data
            return cart_items
        except Exception as e:
            print(e)


class PaymentCredentials(serializers.Serializer):
    razorpay_payment_id  = serializers.CharField(required = True)
    razorpay_signature  = serializers.CharField(required = True)


class CouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(required = True)


class ModifyCartItemsSerializer(serializers.Serializer):
    place_id = serializers.CharField(required = True)
    quantity = serializers.IntegerField(required = True)
    date = serializers.DateField(required = True)
    slot_id = serializers.CharField(required = True)


class OrderAll(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()
    owner = CustomerDetailsSerializer()
    class Meta:
        model = OrderModel
        fields = "__all__"
    def get_cart_items(self, obj):
        cart_items = []
        try:
            cart_obj = OrderModel.objects.get(id = obj.id)
            serializer = OrderItemSerializer(cart_obj.related_cart.all(), many=True)
            cart_items = serializer.data
            return cart_items
        except Exception as e:
            print(e)


class DateSerializer(serializers.Serializer):
    from_date = serializers.DateField(required = True)
    to_date = serializers.DateField(required = True)
