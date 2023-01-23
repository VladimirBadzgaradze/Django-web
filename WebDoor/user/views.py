from io import BytesIO

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files import File
from .models import UserData
import re
import os
import base64
import requests
import datetime


def login_(request):
    error = ''
    if request.method == 'POST':
        username = request.POST['loginName']
        password = request.POST['loginPassword']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not request.POST.get('loginCheck', None):
                request.session.set_expiry(0)

            return redirect('main')

        error = 'Invalid login'

    return render(request, 'user/login.html', {'error': error})


def sign_up(request):
    data = {
        'username': '',
        'email': '',
        'password': '',
        'password2': '',
        'terms': 'checked',

        'user_exist': '',
        'true_email': '',
        'password_strong': '',
        'password_coincidence': '',
        'terms_of_use': ''
    }

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['registerEmail']
        password = request.POST['registerPassword']
        password2 = request.POST['registerRepeatPassword']
        data['username'] = username
        data['email'] = email
        data['password'] = password
        data['password2'] = password2

        if User.objects.filter(username=username).exists():
            data['user_exist'] = 'Username already exist.'
        elif not valid_username(username):
            data['user_exist'] = 'The username can contain only English letters, numbers, char "_", and start with the letter.'

        # email check
        if not email_existing_check(email):
            data['true_email'] = "This email doesn't exist."
        elif User.objects.filter(email=email).exists():
            data['true_email'] = 'This email is already registered.'

        result = password_check(password)
        if not result['password_ok']:
            for k, v in result.items():
                if k != 'password_ok' and v:
                    data['password_strong'] = v
        if password != password2:
            data['password_coincidence'] = "Passwords don't match."
        if request.POST.get('registerCheck', None):
            data['terms_of_use'] = 'You must agree to the terms of usage.'
            data['terms'] = ''

        if not any(list(map(lambda x: bool(data[x]), ['user_exist', 'true_email', 'password_strong', 'password_coincidence', 'terms_of_use']))):

            # EMAIL SEND

            date = datetime.date.today()

            base64_data = base64.b64encode(open(os.path.dirname(os.path.realpath(__file__)) + '/static/user/img/no_photo.jpg', 'rb').read()).decode('utf-8')

            user_data = UserData(username=username, reg_date=date, photo_txt=base64_data)
            user_data.save()

            user = User.objects.create_user(username, email, password)

            login(request, user)

            return redirect('main')

    return render(request, 'user/register.html', data)


def valid_username(name):
    return not name[0].isdigit() and all(c.isalnum() or c == '_' for c in name)


def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    # overall result
    password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)

    return {
        'password_ok': password_ok,
        'length_error': 'The password must be at least 8 characters long.' if length_error else None,
        'digit_error': 'The password must contain at least 1 digit.' if digit_error else None,
        'uppercase_error': 'The password must contain at least 1 capital letter.' if uppercase_error else None,
        'lowercase_error': 'The password must contain at least 1 lowercase letter.' if lowercase_error else None,
        'symbol_error': 'The password must contain at least 1 special character.' if symbol_error else None,
    }


def email_existing_check(email):
    response = requests.get(
        "https://isitarealemail.com/api/email/validate",
        params={'email': email})

    status = response.json()['status']
    if status == "valid":
        return True
    return False


@login_required
def profile(request, uname):
    data = {
        'req_un': User.objects.get_by_natural_key(request.user).username,
        'username': uname,
        'email': User.objects.get_by_natural_key(uname).email,
        'udata':  UserData.objects.get(username=User.objects.get_by_natural_key(uname).username)

    }
    return render(request, 'user/profile.html', data)


def logout_(request):
    logout(request)
    return redirect('main')
