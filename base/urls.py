
from django.urls import path
from . import views
from django.contrib.auth import views as django_auth_views

urlpatterns = [

    path('', views.home, name='home'),
    path('login/', views.log_in, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.register, name='register'),

   
    path('room/<str:pk>/', views.room, name='room'),
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),

    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<str:pk>/', views.updateRoom, name='update-room'),
    path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room'),
    path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
    path('update-user/', views.updateUser, name='update-user'),
    path('topics/', views.topicsPage, name='topics'),
    path('recent-activity/', views.activityPage, name='recent-activity'),

    path('changepassword/', views.password_change, name='password_change'),
    path('activate/<uidb64>/<token>/', views.verify_email_address,name='activate'),
    path('resetpassword/', django_auth_views.PasswordResetView.as_view(template_name = 'base/requestpasswordreset.html'), name='password_reset'),
     path('resetpassword/', django_auth_views.PasswordResetView.as_view(template_name = 'base/requestpasswordreset.html'), name='password_reset'),
    path('resetpasswordsent/', django_auth_views.PasswordResetDoneView.as_view(template_name = 'base/passwordresetsent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', django_auth_views.PasswordResetConfirmView.as_view(template_name = 'base/resetpassword.html'), name='password_reset_confirm'),
    path('reset/done/', django_auth_views.PasswordResetCompleteView.as_view(template_name = 'base/passwordresetdone.html'), name='password_reset_complete'),

]