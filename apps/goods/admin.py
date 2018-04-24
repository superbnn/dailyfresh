from django.contrib import admin

# Register your models here.
from apps.goods.models import *

# class GoodsSPUAdmin(admin.ModelAdmin):
#     '''注册管理类'''
#     list_display = ['desc']


class GoodsCategoryAdmin(admin.ModelAdmin):
    '''管理商品种类'''
    list_display = ['name', 'logo', 'image']

# admin.site.register(GoodsSPU, GoodsSPUAdmin)
admin.site.register(GoodsSPU)
admin.site.register(GoodsCategory, GoodsCategoryAdmin)
# admin.site.register(GoodsCategory)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexSlideGoods)
admin.site.register(IndexCategoryGoods)
admin.site.register(IndexPromotion)
