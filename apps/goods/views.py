from django.core.cache import cache
from django.shortcuts import render

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, GoodsSKU, IndexCategoryGoods


class BaseCartView(View):

    def get_cart_count(self, request):
        '''获取商品购物车数据'''

        # 未登录，购物车商品数为0
        cart_count = 0

        # 用户已登录
        if request.user.is_authenticated():
            key = 'cart_%s' % request.user.id
            strict_redis = get_redis_connection()  # type: StrictRedis
            counts = strict_redis.hvals(key)
            for count in counts:
                cart_count += int(count)  # count为bytes类型
        return cart_count

class IndexView(BaseCartView):

    def get(self, request):
        '''进入首页'''

        # 读取缓存
        context = cache.get('index_page_data')

        # 判断是否有缓存
        if not context:
            '''没有缓存，从数据库中读取'''
            # 全部商品分类图
            categories = GoodsCategory.objects.all()

            # 首页轮播图片
            slide_skus = IndexSlideGoods.objects.all().order_by('index')

            # 商品促销活动
            promotions = IndexPromotion.objects.all().order_by('index')[0:2]

            # 商品分类展示
            for category in categories:
                # 查询显示方式为文字的该类商品
                text_skus = IndexCategoryGoods.objects.filter(category=category, display_type=0).order_by(('index'))
                # 查询显示方式为图片的该类商品
                img_skus = IndexCategoryGoods.objects.filter(category=category, display_type=1).order_by('index')[0:4]

                # 动态增加实例类属性
                category.text_skus = text_skus
                category.img_skus = img_skus

            # 定义字典数据
            context = {
                'categories': categories,
                'slide_skus': slide_skus,
                'promotions': promotions,
            }

            # 缓存数据
            cache.set('index_page_data', context, 60*30)

        # 购物车数量
        cart_count = self.get_cart_count(request)

        context['index_page_data'] = cart_count

        # 响应请求，返回页面
        return render(request, 'index.html', context)