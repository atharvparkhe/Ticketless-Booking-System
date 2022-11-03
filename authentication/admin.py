from django.contrib import admin
from .models import *

# Customer Model
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ["email", "f_name", "l_name", "is_verified"]
admin.site.register(CustomerModel, CustomerModelAdmin)


# Seller Model
admin.site.register(CounterUserModel)