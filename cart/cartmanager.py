#coding=utf-8

from collections import OrderedDict
from django.db import models
from django.db.models import F

from cart.models import CartItem


class CartManager(object):
    def add(self,goodid,colorid,sizeid,count,*args,**kwargs):
        '''添加商品，如果商品已经存在就更新商品的数量(self.update())，否则直接放到购物车'''
        pass

    def delete(self,goodid,colorid,sizeid,*args,**kwargs):
        '''删除一个购物项'''
        pass

    def update(self,goodid,colorid,sizeid,count,step,*args,**kwargs):
        '''更新购物项的数据,添加减少购物项数据'''
        pass

    def queryAll(self,*args,**kwargs):
        ''':return CartItem  多个购物项'''
        pass

#当前用户未登录
class SessionCartManager(CartManager):

    cart_name = 'cart'
    def __init__(self,session):
        self.session = session
        # 创建购物车 #  {cart:{key1:cartitem},{key2:cartitem}}
        if self.cart_name not in self.session:
            self.session[self.cart_name] = OrderedDict()


    def __get_key(self,goodid,colorid,sizeid):
        return goodid+','+colorid+','+sizeid



    def add(self,goodid,colorid,sizeid,count,*args,**kwargs):

        #获取购物项的唯一标示
        key = self.__get_key(goodid,colorid,sizeid)

        # session('cart',[{key1:cartitem,key2:cartitem}])
        if key in self.session[self.cart_name]:
            self.update(goodid,colorid,sizeid,count,*args,**kwargs)
        else:
            self.session[self.cart_name][key] = CartItem(goodid=goodid,colorid=colorid,sizeid=sizeid,count=count)



    def delete(self,goodid,colorid,sizeid,*args,**kwargs):
        key = self.__get_key(goodid,colorid,sizeid)
        if key in self.session[self.cart_name]:
            del self.session[self.cart_name][key]


    def update(self,goodid,colorid,sizeid,step,*args,**kwargs):

        key = self.__get_key(goodid,colorid,sizeid)
        if key in self.session[self.cart_name]:
            cartitem = self.session[self.cart_name][key]
            cartitem.count = int(str(cartitem.count))+int(step)


        else:
            raise Exception('SessionManager中的update出错了')



    def queryAll(self,*args,**kwargs):
        return self.session[self.cart_name].values()

    def migrateSession2DB(self):
        if 'user' in self.session:
            user = self.session.get('user')
            for cartitem in self.queryAll():
                if CartItem.objects.filter(goodid=cartitem.goodid,colorid=cartitem.colorid,sizeid=cartitem.sizeid).count()==0:
                    cartitem.user = user
                    cartitem.save()
                else:
                    item = CartItem.objects.get(goodid=cartitem.goodid,colorid=cartitem.colorid,sizeid=cartitem.sizeid)
                    item.count = int(item.count)+int(cartitem.count)
                    item.save()

            del self.session[self.cart_name]


#用户已登录
class DBCartManger(CartManager):
    def __init__(self,user):
        self.user = user

    def add(self,goodid,colorid,sizeid,count,*args,**kwargs):


        if self.user.cartitem_set.filter(goodid=goodid,colorid=colorid,sizeid=sizeid).count()==1:

            self.update(goodid,colorid,sizeid,count,*args,**kwargs)
        else:
            CartItem.objects.create(goodid=goodid,colorid=colorid,sizeid=sizeid,count=count,user=self.user)



    def delete(self,goodid,colorid,sizeid,*args,**kwargs):
        self.user.cartitem_set.filter(goodid=goodid,colorid=colorid,sizeid=sizeid).update(count=0,is_delete=True)


    def update(self,goodid,colorid,sizeid,step,*args,**kwargs):

        self.user.cartitem_set.filter(goodid=goodid,colorid=colorid,sizeid=sizeid).update(count=F('count')+int(step),is_delete=False)

    def queryAll(self,*args,**kwargs):

        return self.user.cartitem_set.order_by('id').filter(is_delete=False).all()

    #获取当前用户下的所有购物项
    def get_cartitems(self,goodid,sizeid,colorid,*args,**kwargs):
        return self.user.cartitem_set.get(goodid=goodid,sizeid=sizeid,colorid=colorid)



# 工厂方法
#根据当前用户是否登录返回相应的CartManger对象
def getCartManger(request):
    if request.session.get('user'):
        #当前用户已登录
        return DBCartManger(request.session.get('user'))
    return SessionCartManager(request.session)


















