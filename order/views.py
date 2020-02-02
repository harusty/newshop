import logging
import traceback

import jsonpickle as jsonpickle
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradeCreateModel import AlipayTradeCreateModel
from alipay.aop.api.request.AlipayTradeCreateRequest import AlipayTradeCreateRequest
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.response.AlipayTradeCreateResponse import AlipayTradeCreateResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from cart.cartmanager import CartManager, getCartManger
from cart.models import CartItem
from good.models import Inventory
from order.models import Order, OrderItem
from userapp.models import Address
from utils.alipay import *


class ToOrderView(View):
    def get(self,request):
        orderList = request.GET.get('cartitems','')
        userInfo = request.session.get('user','')
        if userInfo:
            return HttpResponseRedirect('/order/order.html?cartitems='+orderList)
        else :
            return render(request,'login.html',{'redirect':'order','cartitems':orderList})


class OrderListView(View):
    def get(self,request):
        cartitems = request.GET.get('cartitems','')
        # 将json格式的字符串放到列表里面
        cartItemList = jsonpickle.loads("["+cartitems+"]")

        # 所有的购物车项目
        cartObjList = [getCartManger(request).get_cartitems(** item) for item in cartItemList if item]

        # 获取用户的地址信息
        address = request.session.get('user').address_set.get(is_default=True)

        # 获取总金额
        totalPrice = 0

        for cartObjItem in cartObjList:
            totalPrice += cartObjItem.getTotalPrice()

        return render(request,'order.html',{'cartObjList':cartObjList,'address':address,'totalPrice':totalPrice })


# 创建阿里pay方法2016102000727201
alipay = AliPay(appid='2016102000727201', app_notify_url='http://127.0.0.1:8000/order/checkPay/', app_private_key_path='order/keys/my_private_key.txt',
                 alipay_public_key_path='order/keys/alipay_public_key.txt', return_url='http://127.0.0.1:8000/order/checkPay/', debug=True)
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s %(levelname)s %(message)s',
#     filemode='a',)
# logger = logging.getLogger('')





class ToPayView(View):
    def get(self,request):
        import uuid, datetime
        # 1 插入order表中的数据
        data = {
            'out_trade_num': uuid.uuid4().hex,
            'order_num':datetime.datetime.today().strftime('%Y%m%d%H%M%S'),
            'payway':request.GET.get('payway','alipay'),
            'address':Address.objects.get(id=request.GET.get('address','')),
            'user':request.session.get('user','')
        }

        orderObj = Order.objects.create(**data)
         # 2 插入orderItem表
        cartitems = jsonpickle.loads(request.GET.get('cartitems'))

        orderItemList = [OrderItem.objects.create(order=orderObj,**cartItem) for cartItem in cartitems if cartItem]


        params =  alipay.direct_pay('胡海强超市',orderObj.out_trade_num,request.GET.get('totalPrice'))
        url = alipay.gateway+'?'+params
        return HttpResponseRedirect(url)


class CheckPay(View):
    def get(self,request):
        # 校验是否支付成功
        params = request.GET.dict()
        print('param====='+str(params))
        # 获取签名
        sign = params.pop('sign')
        print('sign=====' + sign)

        if alipay.verify(params,sign):
            print('sign'+'验证通过')
            # 修改order的状态
            out_trade_num = params.pop('out_trade_num','')
            orderObj = Order.objects.get(out_trade_num=out_trade_num)
            orderObj.status='待发货'
            orderObj.save()

            # 修改购物车对应的表
            orderItemlist = orderObj.orderitem_set.all()
            for orderItem in orderItemlist:
                cartItem = CartItem.objects.get(user=request.session.get('user',''),
                                                goodid= orderItem.goodid,
                                                sizeid=orderItem.sizeid,
                                                colorid=orderItem.colorid,
                                                count=orderItem.count
                                                )
                # 匹配成功 修改购物车
                if cartItem:
                    cartItem.is_delete = True
                    cartItem.save()

                inventoryItem = Inventory.objects.get(goods_id=orderItem.goodid,
                                                size_id=orderItem.sizeid,
                                                color_id=orderItem.colorid,
                                                )
                if inventoryItem:
                    inventoryItem.count -= cartItem.count
                    inventoryItem.save()


            return HttpResponse('out_trade_num==='+out_trade_num)

        return HttpResponse('out_trade_num==='+'支付失败')