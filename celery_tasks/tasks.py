# # 在celery服务器所在的项目中，
# # 需要手动初始化django环境
# # 在celery服务器端所在的项目添加如下代码
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# django.setup()


from celery import Celery
from django.core.mail import send_mail
from django.template import loader

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods
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


@app.task
def generate_static_index_html():
    '''封装产生静态页面的方法'''

    # 全部商品分类图
    categories = GoodsCategory.objects.all()

    # 首页轮播图片
    slide_skus = IndexSlideGoods.objects.all().order_by('index')

    # 商品促销活动
    promotions = IndexPromotion.objects.all().order_by('index')

    # 商品分类展示
    for category in categories:
        # 查询显示方式为文字的该类商品
        text_skus = IndexCategoryGoods.objects.filter(category=category, display_type=0).order_by(('index'))
        # 查询显示方式为图片的该类商品
        img_skus = IndexCategoryGoods.objects.filter(category=category, display_type=1).order_by('index')

        # 动态增加实例类属性
        category.text_skus = text_skus
        category.img_skus = img_skus

    # 获取购物车商品数量(由于是为登录，cart_count = 0)
    cart_count = 0

    # 定义字典数据
    context = {
        'categories': categories,
        'slide_skus': slide_skus,
        'promotions': promotions,
        'cart_count': 0,
    }

    # 获取模板
    template = loader.get_template('index.html')

    # 渲染模板
    html_str = template.render(context)

    # 生成一个叫做index.html的文件，放在桌面的static目录下
    file_path = '/home/python/Desktop/static/index.html'
    with open(file_path, 'w') as file:
        file.write(html_str)
