from django.contrib import admin
from .models import *


class PlacesImageAdmin(admin.StackedInline):
    model = PlaceImagesModel

class TimeSlotModelAdmin(admin.StackedInline):
    model = TimeSlotModel

class PlacesModelAdmin(admin.ModelAdmin):
    # list_display = ["name", "price", "is_available"]
    inlines = [PlacesImageAdmin, TimeSlotModelAdmin]
    class Meta:
        model = PlaceModel

admin.site.register(PlaceModel, PlacesModelAdmin)
