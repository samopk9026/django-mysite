from django.core.handlers.wsgi import WSGIRequest
from django.db import models
import pymysql
import json
from django.http import HttpResponse, JsonResponse
import hashlib
import time


class userInfo:
    def __init__(self, username, password, email='ironman@gmail.com'):
        self.username = username
        self.password = password
        self.email = email

    def gen_token(self) -> str:
        return str(hash(self.username)) + str(hash(self.password)) + str(hash(self.email))

    def diction(self) -> dict:
        return {'username': self.username, 'password': self.password, 'email': self.password}


class ios_login_response:
    def __init__(self, token, error):
        self.error = error
        self.token = token


class database:
    def __init__(self):
        return

    def connect(self):
        self.dataBase = pymysql.connect(
            host='172.22.184.103',
            user='root',
            password='tcTestMysql;',
            database='test_for_auth',
        )

    # 注册
    def register(self, user_info):
        self.connect()
        username = user_info.username
        email = user_info.email
        password = user_info.password
        with self.dataBase:
            with self.dataBase.cursor() as curcor:
                sql = "INSERT INTO `user_info` (`username`, `password`, `email`) VALUES (%s, %s, %s);"
                curcor.execute(sql, (username, password, email))
            self.dataBase.commit()

    # 修改密码
    def changePassword(self, user_id, newpassword):
        self.connect()
        with self.dataBase:
            with self.dataBase.cursor() as curcor:
                sql = "UPDATE `user_info` SET `password` = %s WHERE `id` = %s;"
                curcor.execute(sql, (newpassword, user_id))
            self.dataBase.commit()

    def change_user_description(self, username, new_description):
        self.connect()
        with self.dataBase.cursor() as curcor:
            sql = "UPDATE `user_info` SET `user_description` = %s WHERE `username` = %s"
            curcor.execute(sql, (new_description, username))
        self.dataBase.commit()

    # try to login
    def login(self, user_info, token) -> bool:
        self.connect()
        with self.dataBase.cursor() as cursor:
            sql = "SELECT `id` FROM `user_info` WHERE (`username` = %s and `password` = %s)"
            cursor.execute(sql, (user_info.username, user_info.password))
            result = cursor.fetchone()
            if result is not None:
                sql = "insert into `tokens` (`type`, `token`, `deadline`, `owner`) values (%s, %s, %s, %s)"
                tokenparts = breakdowntoken(token)
                cursor.execute(sql,
                               (tokenparts['type'], tokenparts['token'], tokenparts['deadline'], user_info.username))
                self.dataBase.commit()
                return True
            else:
                return False

    # check if the account has already been registered.(unique username)
    def checkingexistence(self, username) -> bool:
        self.connect()
        with self.dataBase:
            with self.dataBase.cursor() as cursor:
                sql = "SELECT `id` FROM `user_info` WHERE `username` = %s"
                cursor.execute(sql, username)
                result = cursor.fetchone()
                if result is not None:
                    return True
                else:
                    return False

    # check if token is available.
    def tokenisavalible(self, token) -> bool:
        if token is None:
            return False
        t = time.time()  # get current time
        self.connect()
        with self.dataBase.cursor() as cursor:
            tokenparts = breakdowntoken(token)
            sql = "SELECT `owner` FROM `tokens` WHERE (`type` = %s and `token` = %s and `deadline` = %s)"
            cursor.execute(sql, (tokenparts['type'], tokenparts['token'], tokenparts['deadline']))
            result = cursor.fetchone()
            if int(tokenparts['deadline']) > t and result is not None:
                return True
            else:
                return False

    # get user's description
    def get_userdiscription(self, id) -> str:
        self.connect()
        with self.dataBase.cursor() as cursor:
            sql = "SELECT `user_description` FROM `user_info` WHERE `id` = %s"
            cursor.execute(sql, id)
            result = cursor.fetchone()
            self.dataBase.close()
            return result[0]

    # get user's information
    def get_user_info(self, username) -> dict:
        self.connect()
        with self.dataBase.cursor() as cursor:
            sql = "SELECT * FROM `user_info` WHERE `username` = %s"
            cursor.execute(sql, username)
            result = cursor.fetchone()
        return {'username': result[1], 'password': result[2], 'email': result[3], 'user_description': result[4]}

    # get user's username.
    def get_username(self, token) -> str:
        self.connect()
        tokenparts = breakdowntoken(token)
        with self.dataBase.cursor() as cursor:
            sql = "select `owner` from `tokens` where(`type` = %s and `token` = %s)"
            cursor.execute(sql, (tokenparts['type'], tokenparts['token']))
            result = cursor.fetchone()
            return result[0]

    # logout from current page.
    def logout(self, token):
        tokenparts = breakdowntoken(token)
        self.connect()
        with self.dataBase.cursor() as cursor:
            sql = "delete from `tokens` WHERE (`token` = %s and  `type` = %s)"
            cursor.execute(sql, (tokenparts['token'], tokenparts['type']))
            self.dataBase.commit()

    def add_available(self, token):
        self.connect()
        with self.dataBase.cursor() as cursor:
            sql = "insert into `availabletoken` (`tokens`) value (%s)"
            cursor.execute(sql, token)
            self.dataBase.commit()

    def haswebendtoken(self, token) -> bool:
        if token is None:
            return False
        self.connect()
        with self.dataBase.cursor() as cursor:
            tokenparts = breakdowntoken(token)
            currenttime = time.time()
            if int(tokenparts['deadline']) > currenttime:
                sql = "SELECT * FROM `availabletoken` WHERE `tokens`=%s"
                cursor.execute(sql, token)
                result = cursor.fetchone()
                if result is None:
                    return False
                else:
                    return True

    def updatetoken(self, token, username):
        self.connect()
        with self.dataBase.cursor() as cursor:
            tokenparts = breakdowntoken(token)
            sql = "insert into `tokens` (`token`, `deadline` , `owner`, `type` )values (%s, %s, %s, %s)"
            cursor.execute(sql, (tokenparts['token'], tokenparts['deadline'], username, tokenparts['type']))
            self.dataBase.commit()

    def deletewebendtoken(self, token):
        self.connect()
        with self.dataBase.cursor() as cursor:
            sql = "delete from `availabletoken` WHERE `tokens` = %s"
            cursor.execute(sql, (token,))
            self.dataBase.commit()

    def get_watch_action(self, token):
        self.connect()
        owner = self.get_username(token)
        with self.dataBase.cursor() as cursor:
            sql = "SELECT * FROM `watch_action_log` WHERE `owner`=%s"
            cursor.execute(sql, owner)
            result = cursor.fetchone()
            return result

    def update_watch_action(self, token, status):
        self.connect()
        owner = self.get_username(token)
        with self.dataBase.cursor() as cursor:
            if status == "do":
                sql = "UPDATE `watch_action_log` SET `status` = %s WHERE `owner` = %s"
                cursor.execute(sql, ('done', owner))
                self.dataBase.commit()
            elif status == "nottodo":
                sql = "UPDATE `watch_action_log` SET `status` = %s WHERE `owner` = %s"
                cursor.execute(sql, ('fail', owner))
                self.dataBase.commit()


# generate new token for webend
def gen_token(user_info, divicetype: str, lifespan: int) -> str:
    t = time.time() + lifespan
    secretWord = 'i''m ironman'
    sh2 = hashlib.sha3_512()
    token = str(user_info.gen_token) + str(hash(secretWord))
    sh2.update(str(token).encode('utf-8'))
    token = divicetype + '#' + str(int(t)) + '#' + sh2.hexdigest()
    return token


# ios端登陆接口
def ios_login(request: WSGIRequest):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        username = data['username']
        password = data['password']
        user_info = userInfo(username, password)
        data = database()
        token = gen_token(user_info, 'iphone', 100 * 3600)
        if data.checkingexistence(username):
            if data.login(user_info, token):
                response = ios_login_response(token, "")
                return JsonResponse(response.__dict__)
            else:
                response = ios_login_response(token, 'access failure!')
                return JsonResponse(response.__dict__)
        else:
            response = ios_login_response(token="", error='account dose not exist')
            print(response.__dict__)
            return JsonResponse(response.__dict__)


# ios端刷新数据接口
def ios_refresh(request):
    if request.method == "POST":
        token = json.loads(request.body.decode())["token"]
        type = json.loads(request.body.decode())["refreshtype"]
        data = database()
        if type == "refresh":
            if data.tokenisavalible(token):
                info = data.get_user_info(data.get_username(token))
                return JsonResponse(info)
            else:
                return JsonResponse({"None": "666"})
        elif type == "checktoken":
            if data.tokenisavalible(token):
                return JsonResponse({'status': 'true'})
            else:
                return JsonResponse({'status': 'false'})
        elif type == "logout":
            if data.tokenisavalible(token):
                data.logout(token)
                return JsonResponse({'status': 'logout!'})
            else:
                return JsonResponse({'status': 'logout!'})
        elif type == 'get_watch_action':
            if data.tokenisavalible(token):
                result = data.get_watch_action(token)
                # print(result[2])
                if result is None:
                    return JsonResponse({'action': 'none', 'status': ''})
                elif str(result[2]) == '101':
                    return JsonResponse({'action': 'modify your user description', 'status': result[1]}, )
                else:
                    return JsonResponse({'action': 'none', 'status': result[1]})
            else:
                return JsonResponse({'action': 'none'})
        elif type == 'confirm_action':
            if data.tokenisavalible(token):
                result = data.get_watch_action(token)
                if result is not None:
                    if str(result[2]) == '101':
                        data.change_user_description(data.get_username(token), result[3])
                        data.update_watch_action(token, 'do')
                        return JsonResponse({'status': 'succeed'})
                else:
                    JsonResponse({'status': 'failed'})
            else:
                JsonResponse({'status': 'failed'})
        elif type == 'confirm_notact':
            if data.tokenisavalible(token):
                result = data.get_watch_action(token)
                if result is not None:
                    if str(result[2]) == '101':
                        data.update_watch_action(token, 'nottodo')
                        return JsonResponse({'status': 'succeed'})
                else:
                    JsonResponse({'status': 'failed'})
            else:
                JsonResponse({'status': 'failed'})


# 从ios端注册接口
def ios_register(request):
    if request.method == "POST":
        username = json.loads(request.body.decode())["username"]
        password = json.loads(request.body.decode())["password"]
        email = json.loads(request.body.decode())["email"]
        userinfo = userInfo(username, password, email)
        data = database()
        if data.checkingexistence(username):
            return JsonResponse({'result': 'The username has been used!'})
        else:
            data.register(userinfo)
            return JsonResponse({'result': 'register succeed!'})


# ios端扫码登陆web和watch接口
def ios_logintoweb(request):
    if request.method == "POST":
        mytoken = json.loads(request.body.decode())["mytoken"]
        webendtoken = json.loads(request.body.decode())["webendtoken"]
        data = database()
        if mytoken == "not_a_chance":
            data.deletewebendtoken(webendtoken)
            return JsonResponse({'status': 'youaregood'})
        else:
            if data.tokenisavalible(mytoken):
                if data.haswebendtoken(webendtoken):
                    myusername = data.get_username(mytoken)
                    data.updatetoken(webendtoken, myusername)
                    print('youaregood')
                    return JsonResponse({'status': 'youaregood'})
                else:
                    print('webendtoken')
                    return JsonResponse({'status': 'invalid webendtoken'})
            else:
                print('invalid')
                return JsonResponse({'status': 'invalid token'})


# 拆解出token各部分信息
def breakdowntoken(token: str):
    tokenparts = token.split('#')
    Token = {'type': tokenparts[0], 'deadline': tokenparts[1], 'token': tokenparts[2]}
    return Token


def check_qrlogin_status(request):
    if request.method == 'POST':
        token = request.body.decode().split("=")[1]
        token = token.replace("%23", "#")
        data = database()
        if data.tokenisavalible(token):
            if token[0:3] == 'web':
                return JsonResponse({'status': 'web'})
            elif token[0:5] == 'watch':
                return JsonResponse({'status': 'watch'})
        elif not data.haswebendtoken(token):
            return JsonResponse({'status': 'rejected'})
        else:
            return JsonResponse({'status': 'not available!'})
    else:
        return JsonResponse({'status': 'not available'})


def check_action_status(request):
    if request.method == 'POST':
        token = request.body.decode().split("=")[1]
        token = token.replace("%23", "#")
        data = database()
        if data.tokenisavalible(token):
            result = data.get_watch_action(token)
            if result[1][-1] != 'd' and result[1] != 'todo':
                data.update_watch_action(token, result[1]+'_read')
            return JsonResponse({'status': result[1]})
        else:
            return JsonResponse({'status': 'not available'})
    else:
        return JsonResponse({'status': 'not available'})
