from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

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
                text_skus = IndexCategoryGoods.objects.filter(category=category, display_type=0).order_by('index')
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

        context['cart_count'] = cart_count

        # 响应请求，返回页面
        return render(request, 'index.html', context)


class DetailView(BaseCartView):

    def get(self, request, sku_id):
        '''显示商品详情'''

        # 查询所有商品分类信息
        categories = GoodsCategory.objects.all()

        # 查询商品信息,若查询不到就跳回首页
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 查询最新商品信息
        new_skus = GoodsSKU.objects.filter(category=sku.category).order_by('-create_time')[0:2]

        # 获取购物车商品数量
        cart_count = self.get_cart_count(request)

        # 查询同类型其他商品
        other_skus = sku.spu.goodssku_set.exclude(id=sku.id)
        # other_skus = GoodsSKU.objects.filter(spu=sku.spu).exclude(id=sku.id)

        # 保存浏览记录（针对已登录用户）
        if request.user.is_authenticated():
            user_id = request.user.id
            key = 'history_%s' % user_id
            strict_reids = get_redis_connection('default') # type:StrictRedis
            # 删除之前的所有记录
            strict_reids.lrem(key, 0, sku.id)
            # 保存新的记录
            strict_reids.lpush(key, sku.id)
            # 最多只保存5条记录,包含头尾
            strict_reids.ltrim(key, 0, 4)

        # 定义字典数据
        context = {
            'categories': categories,
            'sku': sku,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'other_skus': other_skus,
        }
        return render(request, 'detail.html', context)


class ListView(BaseCartView):

    def get(self, request, cid, page_num):
        '''显示商品列表页'''

        # 获取请求参数
        sort = request.GET.get('sort')

        # 获取商品类别，校验参数合法性
        try:
            category = GoodsCategory.objects.get(id=cid)
        except GoodsCategory.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 获取最新商品信息
        try:
            new_skus = category.goodssku_set.order_by('-create_time')[0:2]
        except:
            new_skus = None

        # 获取全部商品分类数据
        categories = GoodsCategory.objects.all()

        # 获取购物车数据
        cart_count = self.get_cart_count(request)

        # 获取商品列表数据
        if sort == 'price':
            skus = category.goodssku_set.order_by('price')

        elif sort == 'sales':
            skus = category.goodssku_set.order_by('-sales')

        else:
            skus = category.goodssku_set
            sort = 'default'

        page_num = int(page_num)  # 正则表达式分组匹配结果为字符串类型
        # 创建分页对象
        paginator = Paginator(skus, 2)

        # 获取当前页数据
        try:
            page = paginator.page(page_num)
        except EmptyPage:
            page = paginator.page(1)
        # print(type(page_num))

        # 获取页数列表
        page_list = paginator.page_range

        # 定义字典数据
        context = {
            'categories': categories,
            'category': category,
            'new_skus': new_skus,
            'page': page,
            'cart_count': cart_count,
            'sort': sort,
            'page_list': page_list,
        }
        return render(request, 'list.html', context)