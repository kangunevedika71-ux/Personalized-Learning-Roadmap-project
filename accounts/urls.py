from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('verify/', views.verify_otp_view, name='verify-otp'),
    path('verify/resend/', views.resend_otp_view, name='resend-otp'),
    path('verify/change/', views.change_number_view, name='change-number'),
    path('logout/', views.logout_view, name='logout'),
]
