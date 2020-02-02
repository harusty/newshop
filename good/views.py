# Create your views here.
import math

from django.shortcuts import render
from django.views import View

from good.models import Category, Goods
from django.core.paginator import Paginator


class IndexView(View):

    def get(self, request, categoryId=2, num=1):

        categoryId = int(categoryId)
        num = int(num)
        catetorys = Category.objects.all().order_by("id")
        goods = Goods.objects.filter(category_id=categoryId).order_by("id")

        pager = Paginator(goods, 8)

        pageGoods = pager.page(num)

        begin = num - int(math.ceil(10.0 / 2))
        if begin < 1:
            begin = 1

        end = begin + 9
        if end > pager.num_pages:
            end = pager.num_pages

        if end <= 10:
            begin = 1
        else:
            begin = end - 9

        pagegoods = range(begin, end + 1)

        return render(request, 'index.html',
                      {"categorys": catetorys, "goods": pageGoods, "currentId": categoryId, "pagegoods": pagegoods,
                       "currentNum": num})


def recommendView(func):
    def wrapper(goodDetailView, request, goodid, *args, **kwargs):

        # 将存放在cookie中的goodid获取到
        cookieListStr = request.COOKIES.get('recommend','')

        # id的list
        goodidList = [gid for gid in cookieListStr.split() if gid.strip()]

        # 最终推荐的商品
        gooidObjList = [Goods.objects.get(id=gsid) for gsid in goodidList if gsid != goodid
                        and Goods.objects.get(id=gsid).category_id == Goods.objects.get(id=goodid).category_id][:4]

        # 将goodobjList传递给get方法
        response = func(goodDetailView, request, goodid, gooidObjList,*args, **kwargs)
        # 判断goodid是否存在goodidList中。

        if (goodid in goodidList):
            goodidList.remove(goodid)
            goodidList.insert(0, goodid)
        else:
            goodidList.insert(0, goodid)

        # 将goodidList中的数据保存到cook ie中
        response.set_cookie('recommend', ' '.join(goodidList), max_age=3 * 24 * 60 * 60)

        return response

    return wrapper


class GoodsDetailsView(View):
    @recommendView
    def get(self, request, goodsid, recommendList=[]):
        goodsid = int(goodsid)

        goods = Goods.objects.get(id=goodsid)

        return render(request, 'detail.html', {'goods': goods,'recommendList':recommendList})

