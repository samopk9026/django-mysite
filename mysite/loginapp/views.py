from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
import loginapp.models
import qrcode
from io import BytesIO
import base64


# login页面接口
def index(request, messege=''):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_info = loginapp.models.userInfo(username, password)
        data = loginapp.models.database()
        token = loginapp.models.gen_token(user_info, 'web', 3600 * 10)
        if data.checkingexistence(username):
            if data.login(user_info, token):
                direction = redirect('homepage')
                direction.set_cookie('token', token)
                return direction
            else:
                info = request.META.get('REMOTE_HOST')
                userinfo = loginapp.models.userInfo(username=info, password=info)
                token = loginapp.models.gen_token(userinfo, 'web', 10 * 3600)
                data.add_available(token)
                img = qrcode.make(token)
                bank = BytesIO()
                img.save(bank)
                image_stream = bank.getvalue()
                base64stream = base64.b64encode(image_stream).__str__()
                direction = render(request,
                                   template_name='index.html',
                                   context={'messege': 'login failure!!!!!!!',
                                            'qrcode': base64stream[2: len(base64stream) - 1],
                                            'token': token})
                direction.set_cookie('token', token)
                return direction
        else:
            return redirect('register')
    elif request.method == 'GET':
        data = loginapp.models.database()
        token = request.COOKIES.get('token')
        if token is not None:
            data.logout(token)
        info = request.META.get('REMOTE_HOST')
        userinfo = loginapp.models.userInfo(username=info, password=info)
        token = loginapp.models.gen_token(userinfo, 'web', 10 * 3600)
        data.add_available(token)
        img = qrcode.make(token)
        bank = BytesIO()
        img.save(bank)
        image_stream = bank.getvalue()
        base64stream = base64.b64encode(image_stream).__str__()
        direction = render(request,
                           'index.html',
                           context={'messege': messege,
                                    'qrcode': base64stream[2: len(base64stream) - 1],
                                    'token': token})
        direction.set_cookie('token', token)
        return direction


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        user_info = loginapp.models.userInfo(username, password, email)
        data = loginapp.models.database()
        if data.checkingexistence(username):
            return redirect('login')
        else:
            data.register(user_info)
            return redirect('login')
    else:
        return render(request, 'register.html')


def homepage(request):
    token = request.COOKIES.get('token')
    data = loginapp.models.database()
    print(token)
    if token is not None:
        if token.find("#") == -1:
            token = token.replace("%23", "#")
        if data.tokenisavalible(token) and token[0:3] == 'web':
            username = data.get_username(token)
            info = data.get_user_info(username)
            return render(request, template_name='homepage.html', context=info)
        else:
            return redirect('login')
    else:
        return redirect('login')


def qrcodelogin(request):
    data = loginapp.models.database()
    token = request.COOKIES.get('token')
    if data.tokenisavalible(token) and token[0:3] == 'web':
        direction1 = redirect('homepage')
        direction1.set_cookie('token', token)
        return direction1
    else:
        if data.haswebendtoken(token) and token[0:3] == 'web':
            data.deletewebendtoken(token)
        info = request.META.get('REMOTE_HOST')
        userinfo = loginapp.models.userInfo(username=info, password=info)
        token = loginapp.models.gen_token(userinfo, 'web', 10 * 3600)
        data.add_available(token)
        img = qrcode.make(token)
        bank = BytesIO()
        img.save(bank)
        image_stream = bank.getvalue()
        base64stream = base64.b64encode(image_stream).__str__()
        renderr = render(request, 'QRcodelogin.html', {'qrcode': base64stream[2: len(base64stream) - 1],
                                                       'messege': 'scan to login!', 'token': token})
        renderr.set_cookie('token', token)
        return renderr
