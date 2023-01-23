from django.contrib.auth.models import User
from user.models import UserData
from django.core.files import File
from django.shortcuts import render, HttpResponse


def main(request):
    data = {
        'pushed': 'Home',
        'title': 'WebDoor',
        'user': '',
        'email': '',
        'userData': ''
    }
    if request.user.is_authenticated:
        data['user'] = request.user
        data['email'] = User.objects.get_by_natural_key(request.user).email
        try:
            data['userData'] = UserData.objects.get(username=User.objects.get_by_natural_key(request.user).username)
        except Exception:
            pass

    return render(request, 'main/home.html', data)
