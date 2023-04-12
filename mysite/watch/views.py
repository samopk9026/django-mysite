from django.shortcuts import render
import loginapp.models
from django.shortcuts import render, redirect
import qrcode
from io import BytesIO
import base64
from watch.server.server import tend_to_change_description
from django.http import HttpResponse, JsonResponse


def homepage(request):
    try:
        messege = request.COOKIES.get('messege')
    except:
        messege = ''
    token = request.COOKIES.get('token')
    data = loginapp.models.database()
    if token is not None:
        if data.tokenisavalible(token) and token[0:5] == 'watch':
            tend_to_change_description(token, "666", "noaction")
            id = data.get_username(token)
            info = data.get_user_info(id)
            info['messege'] = messege
            return render(request, template_name='template/qrhomepage.html', context=info)
        else:
            return redirect('watchQRcodelogin')
    else:
        return redirect('watchQRcodelogin')


def qrcodelogin(request):
    data = loginapp.models.database()
    token = request.COOKIES.get('token')
    if request.method == "POST":
        data.logout(token)
    # print(token)
    if token is not None:
        if data.tokenisavalible(token) and token[0:5] == 'watch':
            direction1 = redirect('watchhomepage')
            direction1.set_cookie('token', token)
            return direction1
        else:
            if data.haswebendtoken(token):
                data.deletewebendtoken(token)
    info = request.META.get('REMOTE_HOST')
    userinfo = loginapp.models.userInfo(username=info, password=info)
    token = loginapp.models.gen_token(userinfo, 'watch', 36000 * 1000)
    data.add_available(token)
    img = qrcode.make(token)
    bank = BytesIO()
    img.save(bank)
    image_stream = bank.getvalue()
    base64stream = base64.b64encode(image_stream).__str__()
    renderr = render(request, 'QRcodelogin.html', {'qrcode': base64stream[2: len(base64stream) - 1],
                                                   'messege': 'Scan the QRcode to login~',
                                                   'token': token})
    print(token)
    renderr.set_cookie('token', token)
    return renderr


def change_user_description(request):
    if request.method == "POST":
        data = loginapp.models.database()
        token = request.COOKIES.get("token")
        if data.tokenisavalible(token):
            new_description = request.body.decode().split("=")[1].split("%")[0]
            tend_to_change_description(token, new_description, "todo")
            # direction = redirect('watchhomepage')
            # direction.set_cookie('messege', 'Confirm on your phone!')
            # direction.set_cookie('status', 'todo')
            # direction.set_cookie('token', token)
            return JsonResponse({'status': 'good'})
        else:
            # direction = redirect('watchhomepage')
            # direction.set_cookie('messege', 'c')
            # direction.set_cookie('status', 'none')
            return JsonResponse({'status': 'false'})

