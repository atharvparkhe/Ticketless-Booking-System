from rest_framework import serializers
from .models import *


class MultiPlacesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceModel
        fields = ["id", "name", "short_desc", "locality", "price", "img", "ratings"]


class MultiPlaceImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceImagesModel
        fields = ["img"]


class TimeSlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlotModel
        fields = ["start_time", "end_time"]


class SinglePlaceModelSerializer(serializers.ModelSerializer):
    slots = serializers.SerializerMethodField()
    multi_imgs = serializers.SerializerMethodField()
    class Meta:
        model = PlaceModel
        exclude = ["created_at", "updated_at", "capacity"]
    def get_slots(self, obj):
        slots = []
        try:
            place_obj = PlaceModel.objects.get(id = obj.id)
            serializer = TimeSlotsSerializer(place_obj.place_time_slots.all(), many=True)
            slots = serializer.data
            return slots
        except Exception as e:
            print(e)
    def get_multi_imgs(self, obj):
        imgs = []
        try:
            place_obj = PlaceModel.objects.get(id = obj.id)
            serializer = MultiPlaceImagesSerializer(place_obj.place_images.all(), many=True)
            imgs = serializer.data
            return imgs
        except Exception as e:
            print(e)

    