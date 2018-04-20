'''要定义一META类，设置abstract = True'''
from django.db import models


class BaseModel(models.Model):
    """模型类基类"""

    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 最后修改时间
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    class Meta(object):
        # 需要指定基类模型类为抽象的,否则迁移生成表时会出错
        abstract = True

#
# class BaseModel(models.Model):
#     '''定义模型类基类'''
#
#     # 创建时间
#     create_time = models.DateTimeField(auto_now_add=True)
#     # 更新时间
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta(object):
#         '''需要指定基类模型类为抽象的，否则迁移是会报错'''
#         abstract = True