from django.db import models
from base.models import *


class CustomerModel(BaseUser):
    def __str__(self):
        return self.email

class CounterUserModel(BaseUser):
    def save(self, *args, **kwargs):
        self.is_staff = True
        super(CounterUserModel, self).save(*args, **kwargs) 
    def __str__(self):
        return self.email

