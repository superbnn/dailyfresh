# # 在celery服务器所在的项目中，
# # 需要手动初始化django环境
# # 在celery服务器端所在的项目添加如下代码
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()


from celery import Celery
from django.core.mail import send_mail

from dailyfresh import settings
# 创建celery对象 参数1：客户端名称   参数2：指定的broker
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/1')


@app.task
def send_active_email(username, email, token):
    """封装发送邮件方法"""
    subject = "天天生鲜用户激活"  # 标题
    message = ""  # 邮件正文(纯文本)
    sender = settings.EMAIL_FROM  # 发件人
    receivers = [email]  # 接收人, 需要是列表
    # 邮件正文(带html样式)
    html_message = '<h2>尊敬的 %s, 感谢注册天天生鲜</h2>' \
                   '<p>请点击此链接激活您的帐号: ' \
                   '<a href="http://127.0.0.1:8000/users/active/%s">' \
                   'http://127.0.0.1:8000/users/active/%s</a>' \
                   % (username, token, token)
    send_mail(subject, message, sender, receivers, html_message=html_message)
