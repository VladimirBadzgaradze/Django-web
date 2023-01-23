from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_, name='login'),
    path('sing-up', views.sign_up, name='sign-up'),
    path('logout', views.logout_, name='logout'),
    path('profile/<str:uname>', views.profile, name='profile')
]
