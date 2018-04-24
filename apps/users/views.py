import re

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired

from apps.users.models import User
from dailyfresh import settings
from celery_tasks.tasks import *


class RegisterView(View):
    '''定义注册类视图'''

    def get(self, request):
        '''显示注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''后台注册逻辑'''
        # todo
        # 1.获取请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 校验参数合法性
        # 2.判空
        if not all([username, password, password2, email]):
            return render(request, 'register.html', {'errormsg': '参数不完整'})

        # 3.判断两次输入密码是否正确
        if password != password2:
            return render(request, 'register.html', {'errormsg': '两次输入的密码不一致'})

        # 4.是否勾选用户协议
        if allow != 'on':
            return render(request, 'register.html', {'errormsg': '请先同意用户协议'})

        # 5.判断邮箱格式是否正确
        if not re.match('^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'message': '邮箱格式不正确'})

        # 业务逻辑
        # 6.调用Django自带的用户认证模块：一方面可以实现保存用户，另一方面实现隐私信息的加密
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            User.objects.filter(id=user.id).update(is_active=False)
        except IntegrityError:
            return render(request, 'register.html', {'errormsg': '用户名已存在'})

        # todo
        # 7.发送激活邮件
        token = user.generate_active_token()
        # self.send_active_email(username, email, token)
        # 使用celery异步发送激活邮件
        send_active_email.delay(username, email, token)
        # 响应请求，返回HTML页面
        return redirect(reverse('goods:index'))

        # @staticmethod
        # def send_active_email(username, email, token):
        #     """封装发送邮件方法"""
        #     subject = "天天生鲜用户激活"  # 标题
        #     message = ""  # 邮件正文(纯文本)
        #     sender = settings.EMAIL_FROM  # 发件人
        #     receivers = [email]  # 接收人, 需要是列表
        #     # 邮件正文(带html样式)
        #     html_message = '<h2>尊敬的 %s, 感谢注册天天生鲜</h2>' \
        #                    '<p>请点击此链接激活您的帐号: ' \
        #                    '<a href="http://127.0.0.1:8000/users/active/%s">' \
        #                    'http://127.0.0.1:8000/users/active/%s</a>' \
        #                    % (username, token, token)
        #     send_mail(subject, message, sender, receivers, html_message=html_message)


class ActiveView(View):
    '''定义激活邮箱视图'''

    def get(self, request, token):
        try:
            # 判断是否失效
            s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY)
            dict_data = s.loads(token)
        except SignatureExpired:
            return HttpResponse('激活链接已失效')
        # 获取用户ID
        user_id = dict_data.get('confirm')
        # 修改字段为已激活
        User.objects.filter(id=user_id).update(is_active=True)
        # 响应请求
        return redirect(reverse('goods:index'))
        # try:
        #     # 解密token
        #     s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY)
        #     # 字符串 -> bytes
        #     # dict_data = s.loads(token.encode())
        #     dict_data = s.loads(token)
        # except SignatureExpired:
        #     # 判断是否失效
        #     return HttpResponse('激活链接已经失效')
        #
        # # 获取用户id
        # user_id = dict_data.get('confirm')
        # # 修改字段为已激活
        # User.objects.filter(id=user_id).update(is_active=True)


class LoginView(View):
    def get(self, request):
        '''进入登录页面'''
        return render(request, 'login.html')

    def post(self, request):
        '''处理登录逻辑'''
        # todo
        # 1.获取请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        # 2.检验参数合法性
        # 判空
        if not all([username, password]):
            return render(request, 'login.html', {'errormsg': '参数不能为空'})

        # 判断用户是否存在
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'errormsg': '用户名或密码不正确'})

        # 判断用户是否激活
        if user.is_active == False:
            return render(request, 'login.html', {'errormsg': '请先激活账号'})

        # 调用django的login方法，保存用户的登录状态(session)
        login(request, user)

        # 判断是否记住用户名
        if remember != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)
        # 响应请求，返回首页
        return redirect(reverse('goods:index'))


class LogoutView(View):
    def get(self, request):
        '''注销用户'''
        # 由用户认证系统完成，会清理cookie和session数据
        logout(request)
        return redirect(reverse('goods:index'))