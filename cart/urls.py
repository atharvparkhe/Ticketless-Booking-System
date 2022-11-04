from django.urls import path
from . import views
from .views import *

urlpatterns = [
	path('scan-ticket/', views.scan_ticket, name="scan-ticket"),
	path('apply-coupon/', views.apply_coupon, name="apply-coupon"),
	path('book-now/', views.book_now, name="book-now"),
	path('checkout/', views.checkout, name="checkout"),
	path('result/', views.resultPage, name="result"),
]