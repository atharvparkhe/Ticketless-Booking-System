from django.urls import path
from . import views
from .views import *

urlpatterns = [
	path('signup/', views.signUp, name="signup"),
	path('login/', views.logIn, name="login"),
	path('forgot/', views.forgot, name="forgot"),
	path('reset/', views.reset, name="reset"),
	path('resend/forgot/', views.resendForgot, name="resend-forgot"),

	# path('seller-signup/', views.sellersignUp, name="admin-signup"),
	# path('seller-login/', views.sellerlogIn, name="admin-login"),
	# path('seller-login/otp/', views.sellerloginOTP, name="admin-login-otp"),
	# path('seller-forgot/', views.sellerforgot, name="admin-forgot"),
	# path('seller-reset/', views.sellerreset, name="admin-reset"),
	# path('seller-verify/', views.sellerVerify, name="admin-verify"),
	# path('seller-remove/', views.sellerRemove, name="admin-remove"),
	# path('seller-remove-confirm/<uid>/', views.sellerRemoveVerification, name="admin-remove-confirm"),
	# path('seller-list/', views.sellerList, name="seller-list"),

	# path("seller-send-special-email/", views.specialEmail, name="seller-send-special-email"),

	# path("edit-phone/", views.editPhoneNo, name="edit-phone"),
	# path("edit-name/", views.editName, name="edit-name"),
]