from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from itsdangerous import TimedJSONWebSignatureSerializer

from dailyfresh import settings
from utils.models import BaseModel

from django.contrib.auth.models import AbstractUser


class User(BaseModel, AbstractUser):
    """用户信息模型类"""

    def generate_active_token(self):
        '''生成激活令牌'''
        s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 3600)
        token = s.dumps({'confirm': self.id})  # 返回bytes类型
        return token.decode()

    class Meta:
        db_table = 'df_user'


# class TestModel(models.Model):
#     '''测试模型'''
#
#     ORDER_STATUS_CHOICES = (
#         (1, '待支付'),
#         (2, '待发货'),
#         (3, '待收货'),
#         (4, '待评价'),
#         (5, '已完成'),
#     )
#
#     status = models.SmallIntegerField(default=1, verbose_name='订单状态', choices=ORDER_STATUS_CHOICES)
#
#     class Meta(object):
#         db_table = 'df_test'
#         # 指定模型在后台显示的名称
#         verbose_name = '测试模型'
#         # 去除后台显示的名称默认添加的's'
#         verbose_name_plural = verbose_name


class TestModel(models.Model):
    """测试"""

    ORDER_STATUS_CHOICES = (
        (1, "待支付"),
        (2, "待发货"),
        (3, "待收货"),
        (4, "待评价"),
        (5, "已完成"),
    )

    status = models.SmallIntegerField(default=1,
                                      verbose_name='订单状态',
                                      choices=ORDER_STATUS_CHOICES)

    class Meta(object):
        db_table = 'df_test'
        # 指定模型在后台显示的名称
        verbose_name = '测试模型'
        # 去除后台显示的名称默认添加的 's'
        verbose_name_plural = verbose_name


class Address(BaseModel):
    """地址模型类"""

    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, null=True, verbose_name="邮政编码")
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    user = models.ForeignKey(User, verbose_name="所属用户")

    class Meta:
        db_table = "df_address"
        verbose_name = '地址'
        verbose_name_plural = verbose_name