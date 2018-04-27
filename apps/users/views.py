import re
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired
from redis import StrictRedis
from apps.goods.models import GoodsSKU
from apps.users.models import User, Address
from dailyfresh import settings
from celery_tasks.tasks import *
from utils.common import BaseView, LoginRequiredMixin


class RegisterView(BaseView):
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
        next = request.GET.get('next')

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

        # 获取next参数，表示要跳转到哪一个界面
        if next is None:
            response = redirect(reverse('goods:index'))
        else:
            response = redirect(next)
        # 响应请求，返回首页
        return response


class LogoutView(View):
    def get(self, request):
        '''注销用户'''
        # 由用户认证系统完成，会清理cookie和session数据
        logout(request)
        return redirect(reverse('goods:index'))


class UserOrderView(LoginRequiredMixin, View):
    def get(self, request):
        '''进入用户中心订单界面'''
        context = {
            "which_page": 2
        }
        return render(request, 'user_center_order.html', context)


class UserAddressView(LoginRequiredMixin, View):
    def get(self, request):
        '''进入用户中心地址界面'''
        '''展示最新添加的地址'''
        user = request.user

        try:
            # 方式1：可能报IndexError
            # address = Address.objects.filter(user=request.user).order_by('-create_time')[0]

            # 方式2：可能报IndexError
            # address = user.address_set.order_by('-create_time')[0]

            # 方式3：可能报DoesNotExist错误
            address = user.address_set.latest('create_time')
        except Exception:
            address = None
        context = {
            # 不需要主动传，django会自动传
            # 'user':user
            "which_page": 3,
            'address': address,
        }
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        '''新增用户地址'''

        # 获取请求参数
        receiver = request.POST.get('receiver')
        detail = request.POST.get('detail')
        zip_code = request.POST.get('zip_code')
        mobile = request.POST.get('mobile')
        user = request.user

        # 校验参数合法性
        if not all([receiver, detail, mobile]):
            return render(request, 'user_center_site.html', {'errormsg': '请求参数不完整'})

        # 将数据保存到数据库中
        Address.objects.create(
            receiver_name=receiver,
            receiver_mobile=mobile,
            detail_addr=detail,
            zip_code=zip_code,
            user=user,
        )

        # 响应请求
        return redirect(reverse('users:address'))


class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        '''进入用户中心个人信息界面'''
        user = request.user

        # 获取用户最新有地址
        try:
            address = user.address_set.latest('create_time')
        except Exception:
            address = None

        strict_redis = get_redis_connection('default') # type: StrictRedis
        key = 'history_%s' % user.id
        # 注意redis中键值为字符串类型
        sku_ids = strict_redis.lrange(key, 0, 4)
        # print(sku_ids)  二进制类型数据
        skus = []

        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=int(sku_id))
            skus.append(sku)

        print(skus)
        context = {
            "which_page": 1,
            'address': address,
            'skus': skus,
        }

        # 登录检测：下面这种方式太繁琐
        # if request.user.is_authenticated():
        #     return render(request, 'user_center_info.html', context)
        # else:
        #     return redirect(reverse('users:login'))
        return render(request, 'user_center_info.html', context)
