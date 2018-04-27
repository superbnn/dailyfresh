from django.contrib import admin

# Register your models here.
from django.core.cache import cache

from apps.goods.models import *

# class GoodsSPUAdmin(admin.ModelAdmin):
#     '''注册管理类'''
#     list_display = ['desc']
from celery_tasks.tasks import generate_static_index_html


class BaseAdmin(admin.ModelAdmin):
    '''模型管理类'''

    def save_model(self, request, obj, form, change):
        '''在管理后台新增或修改一条数据后调用'''
        super().save_model(request, obj, form, change)
        print('save_model: %s ' % obj)
        # 异步生成静态页面
        generate_static_index_html.delay()
        # 修改了数据库就要删除缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        '''在管理后台删除一条数据时调用'''
        super().delete_model(request, obj)
        print('save_model: %s ' % obj)
        # 异步生成静态页面
        generate_static_index_html.delay()
        # 修改了数据库就要删除缓存
        cache.delete('index_page_data')


class GoodsCategoryAdmin(BaseAdmin):
    '''管理商品种类'''
    list_display = ['name', 'logo', 'image']


class GoodsSPUAdmin(BaseAdmin):
    pass


class GoodsSKUAdmin(BaseAdmin):
    pass


class IndexSlideGoodsAdmin(BaseAdmin):
    pass


class IndexPromotionAdmin(BaseAdmin):
    pass


class IndexCategoryGoodsAdmin(BaseAdmin):
    pass

# admin.site.register(GoodsSPU, GoodsSPUAdmin)
admin.site.register(GoodsSPU, GoodsSPUAdmin)
admin.site.register(GoodsCategory, GoodsCategoryAdmin)
# admin.site.register(GoodsCategory)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(GoodsImage)
admin.site.register(IndexSlideGoods, IndexSlideGoodsAdmin)
admin.site.register(IndexCategoryGoods, IndexCategoryGoodsAdmin)
admin.site.register(IndexPromotion, IndexPromotionAdmin)
