import datetime
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse
from user.models import UserData
import string
import random
import json

from django.views.decorators.csrf import csrf_exempt


@login_required
def get_door(request):
    return render(request, 'management/get_door.html')


@login_required
def my_doors(request):
    data = {
        'pushed': 'Manage Doors',
        'doors': UserData.objects.get(username=request.user).doors.split(';')[1:],
        'activity_delays': [[k, timedelta_to_datetime_str(datetime.datetime.today(), datetime.datetime.fromisoformat(v)), int((datetime.datetime.today() - datetime.datetime.fromisoformat(v)).total_seconds()), *get_params(request.user, k).values()] for k, v in json.loads(UserData.objects.get(username=request.user).last_conn).items()],
        'user': request.user,
        'email': User.objects.get_by_natural_key(request.user).email,
        'userData': UserData.objects.get(username=User.objects.get_by_natural_key(request.user).username)
    }
    return render(request, 'management/my_doors.html', data)


@login_required
def del_door(request, obj_name):
    return HttpResponse('')


@login_required
@csrf_exempt
def manage_door_console(request, obj_name):
    udata = udata_or_none(username=request.user)
    if udata:
        doors = udata.doors.split(';')[1:]
        if obj_name in doors:
            if request.method == 'GET':
                data = {
                    'door_name': obj_name,
                    'user': request.user,
                    'email': User.objects.get_by_natural_key(request.user).email,
                    'userData': UserData.objects.get(username=User.objects.get_by_natural_key(request.user).username)
                }

                return render(request, 'management/manage.html', data)

            if request.POST['update'] == 'true':
                ans = get_answer(request.user, obj_name)
                return HttpResponse(json.dumps({
                    'last_command': get_command(request.user, obj_name),
                    'answer': ans
                }))

            console_text = request.POST['text']
            set_command(request.user, obj_name, console_text)

    return HttpResponse('404')


@login_required
def update_my_doors(request):
    data = {
        'activity_delays': dict([(k, [timedelta_to_datetime_str(datetime.datetime.today(), datetime.datetime.fromisoformat(v)), int((datetime.datetime.today() - datetime.datetime.fromisoformat(v)).total_seconds())]) for k, v in json.loads(UserData.objects.get(username=request.user).last_conn).items()])
    }
    return HttpResponse(json.dumps(data))


def timedelta_to_datetime_str(date_now, date_last):
    total = int((date_now - date_last).total_seconds())

    days = total // (24 * 3600)
    total -= days * 24 * 3600
    hours = total // 3600
    total -= hours * 3600
    minutes = total // 60
    total -= minutes * 60
    seconds = total

    return f'{days}D {hours}H {minutes}M {seconds}S'


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def set_last_conn(username, name):
    udata = UserData.objects.get(username=username)

    jsn_conn = json.loads(udata.last_conn)
    jsn_conn[name] = datetime.datetime.today().isoformat()
    udata.last_conn = json.dumps(jsn_conn)

    udata.save()


def set_new_name(username):
    udata = UserData.objects.get(username=username)
    name = randomword(10)
    while name in udata.doors:
        name = randomword(10)

    udata.doors = ';'.join([udata.doors, name])
    udata.save()
    return name


def set_params(username, name, params):
    udata = UserData.objects.get(username=username)

    jsn_conn = json.loads(udata.doors_params)
    jsn_conn[name] = params
    udata.doors_params = json.dumps(jsn_conn)

    udata.save()


def get_params(username, name):
    udata = udata_or_none(username)

    jsn = json.loads(udata.doors_params)

    if name not in jsn.keys() or not jsn[name]:
        return ''

    params = jsn[name]

    return params


def udata_or_none(username):
    try:
        return UserData.objects.get(username=username)
    except Exception:
        return None


def set_command(username, name, command):
    udata = udata_or_none(username)

    jsn = json.loads(udata.doors_command)

    jsn[name] = command
    udata.doors_command = json.dumps(jsn)
    udata.save()


def get_command(username, name):
    udata = udata_or_none(username)

    jsn = json.loads(udata.doors_command)

    if name not in jsn.keys() or not jsn[name]:
        return ''

    command = jsn[name]

    # we clear data when get answer for it (def set_answer)
    # jsn[name] = ''
    # udata.doors_command = json.dumps(jsn)
    # udata.save()
    return command


def set_answer(username, name, data):
    print('SETTING')
    udata = UserData.objects.get(username=username)

    jsn = json.loads(udata.doors_outputs)
    jsn[name] = data

    udata.doors_outputs = json.dumps(jsn)

    # clear input command
    jsn = json.loads(udata.doors_command)
    jsn[name] = ''
    udata.doors_command = json.dumps(jsn)

    udata.save()


def get_answer(username, name):
    udata = UserData.objects.get(username=username)

    jsn = json.loads(udata.doors_outputs)

    if name not in jsn.keys() or not jsn[name]:
        return ''

    answer = jsn[name]
    jsn[name] = ''

    udata.doors_outputs = json.dumps(jsn)
    udata.save()
    return answer


@csrf_exempt
def data_exchange(request):
    if request.method == 'POST':
        if request.POST['main'] == 'login':
            username = request.POST['username']
            if udata_or_none(username):
                name = set_new_name(username)
                set_params(username, name, {'system_name': request.POST['system_name'], 'bits': request.POST['bits'], 'linkage': request.POST['linkage']})
                set_last_conn(username, name)
                return HttpResponse(json.dumps({'main': 'OK', 'name': name}))
            return HttpResponse(json.dumps({'main': 'error'}))

        elif request.POST['main'] == 'get':
            username = request.POST['username']
            name = request.POST['name']
            if udata_or_none(username):
                set_last_conn(username, name)
                command = get_command(username, name)
                if command:
                    return HttpResponse(json.dumps({'main': 'command', 'command': command}))
                return HttpResponse(json.dumps({'main': 'no_command'}))
            return HttpResponse(json.dumps({'main': 'error'}))

        elif request.POST['main'] == 'post':
            username = request.POST['username']
            name = request.POST['name']
            data = request.POST['data']
            if udata_or_none(username):
                set_last_conn(username, name)
                set_answer(username, name, data)
                return HttpResponse(json.dumps({'main': 'OK'}))
            return HttpResponse(json.dumps({'main': 'error'}))
