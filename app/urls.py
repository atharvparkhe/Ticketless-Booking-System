from django.urls import path
from . import views
from .views import *

urlpatterns = [
	path('all-places/', views.AllPlacesView.as_view(), name="all-places"),
	path('single-place/<id>/', views.SinglePlaceView.as_view(), name="single-place"),
]