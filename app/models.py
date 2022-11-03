from email.policy import default
from django.db import models
from base.models import BaseModel
from .validators import validate_stars

class PlaceModel(BaseModel):
    name = models.CharField(max_length=50)
    short_desc = models.CharField(max_length=500)
    description = models.TextField()
    address = models.TextField()
    price = models.FloatField(default=100)
    video = models.FileField(upload_to="videos", max_length=100)
    capacity = models.SmallIntegerField(default=15)
    ratings = models.FloatField(validators=[validate_stars], default=0)
    lattitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    def __str__(self):
        return self.name


class PlaceImagesModel(BaseModel):
    place = models.ForeignKey(PlaceModel, related_name="place_images", on_delete=models.CASCADE)
    img = models.ImageField(upload_to="imahges", height_field=None, width_field=None, max_length=None)
    def __str__(self):
        return self.place.name
    

class TimeSlotModel(BaseModel):
    place = models.ForeignKey(PlaceModel, related_name="place_time_slot", on_delete=models.CASCADE)
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    end_time = models.TimeField(auto_now=False, auto_now_add=False)
    def __str__(self):
        return self.place.name