from django.urls import path
from . import views

urlpatterns = [
    path('get_door/', views.get_door, name='get-door'),
    # path('file_system/', views.file_system, name='file-system'),

    path('update_my_doors/', views.update_my_doors, name='update-my-doors'),
    path('my_doors/', views.my_doors, name='my-doors'),

    path('manage/<str:obj_name>/console', views.manage_door_console, name='manage'),
    path('delete/<str:obj_name>', views.del_door, name='del_door'),

    path('communication_channel/', views.data_exchange)
]
