from django.db import models


class UserData(models.Model):
    username = models.CharField(max_length=150)
    reg_date = models.DateField()

    photo_txt = models.TextField(default='')

    doors = models.TextField(default='None')

    doors_command = models.TextField(default='{}')  # {'name_door': 'command' }
    doors_outputs = models.TextField(default='{}')
    doors_params = models.TextField(default='{}')
    last_conn = models.TextField(default='{}')

    def __str__(self):
        return self.username
