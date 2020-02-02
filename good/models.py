# -*- coding: utf-8 -*-

# Create your models here.
from django.db import models
# import os,django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newshop.settings")
# django.setup()
# project_name 项目名称 django.setup()


class Category(models.Model):
    cname = models.CharField(max_length=10)

    def __str__(self):
        return u'Category:%s'%self.cname


class Goods(models.Model):
    gname = models.CharField(max_length=100)
    gdesc = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5,decimal_places=2)
    oldprice = models.DecimalField(max_digits=5,decimal_places=2)
    category = models.ForeignKey(Category,on_delete=True)

    def __str__(self):
        return u'Goodname:%s'%self.gname

    # 获取商品的大图，默认第一张
    def getGoodImg(self):
        return self.inventory_set.first().color.colorurl


    # 获取商品所有的颜色
    def getColors(self):
        colors = []
        for inventoryItem in self.inventory_set.all():
            if inventoryItem.color not in colors:
                colors.append(inventoryItem.color)
        return colors

    # 获取商品所有的尺寸对象
    def getSizes(self):
        sizes = []
        for inventoryItem in self.inventory_set.all():
            if inventoryItem.size not in sizes:
                sizes.append(inventoryItem.size)
        return sizes

    def getDatailList(self):
        import collections
        # key详情名称，value图片列表
        datas = collections.OrderedDict()
        for goodDeatail in self.goodsdetail_set.all():
            gdname = goodDeatail.name()
            if not datas.__contains__(gdname):
                datas[gdname] = [goodDeatail.gdurl]
            else:
                datas[gdname].append(goodDeatail.gdurl)

        return datas



class GoodsDetailName (models.Model):
    gdname = models.CharField(max_length=30)


    def __str__(self):
        return u'GoodsDetailName:%s'%self.gdname

class GoodsDetail(models.Model):
    gdurl = models.ImageField(upload_to='')
    gdname = models.ForeignKey(GoodsDetailName,on_delete=True)
    goods = models.ForeignKey(Goods,on_delete=True)

    # 获取详情名称
    def name(self):
        return self.gdname.gdname


class Size(models.Model):
    sname = models.CharField(max_length=10)

    def __str__(self):
        return u'Size:%s'%self.sname


class Color(models.Model):
    colorname = models.CharField(max_length=10)
    colorurl = models.ImageField(upload_to='color/')

    def __str__(self):
        return u'Color:%s' % self.sname

class Inventory(models.Model):
    count = models.PositiveIntegerField()
    color = models.ForeignKey(Color,on_delete=True)
    goods = models.ForeignKey(Goods,on_delete=True)
    size = models.ForeignKey(Size,on_delete=True)


