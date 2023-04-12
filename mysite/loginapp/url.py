from django.template.defaulttags import url
from django.urls import path
from . import views, models

# 访问路径
urlpatterns = [
    path('login/', views.index, name='login'),
    path('register/', views.register, name='register'),
    path('ios/login/', models.ios_login, name='ios_login'),
    path('qrcodelogin/', views.qrcodelogin, name='QRcodelogin'),
    path('homepage/', views.homepage, name='homepage'),
    path('ios/refresh/', models.ios_refresh, name='ios_refresh'),
    path('ios/register/', models.ios_register, name='ios_register'),
    path('ios/logintoweb/', models.ios_logintoweb, name='ios_logintowed'),
    path('ios/logout/', models.ios_refresh, name='ios_logout'),
    path('check_qrlogin_status/', models.check_qrlogin_status, name='check_qrlogin_status'),
    path('check_action_status/', models.check_action_status, name='check_action_status')
]
