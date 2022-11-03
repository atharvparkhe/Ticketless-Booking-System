from django.urls import path
from . import views
from .views import *

urlpatterns = [
	path('scan-ticket/', views.scan_ticket, name="scan-ticket"),
]