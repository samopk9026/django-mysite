from django.urls import path, include
from watch import views
urlpatterns = [
    path('qrcodelogin/', views.qrcodelogin, name='watchQRcodelogin'),
    path('homepage/', views.homepage, name='watchhomepage'),
    path('chang_user_description/', views.change_user_description, name="change_user_description"),
    # path('check_watch_action/', views.check_watch_action, name='check_watch_action')
]