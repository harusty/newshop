from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views import View
from cart import  cartmanager


class AddCartView(View):
    def post(self,request):
        request.session.modified = True
        addCartDict = request.POST.dict()
        flag = request.POST.get('flag','')
        if flag == 'add':
            cartManager = cartmanager.getCartManger(request)
            cartManager.add(**request.POST.dict())
        elif flag == 'plus':
            cartManager =cartmanager.getCartManger(request)
            cartManager.update(step=1,**request.POST.dict())
        elif flag == 'minus':
            cartManager = cartmanager.getCartManger(request)
            cartManager.update(step=-1,**request.POST.dict())
        elif flag == 'delete':
            cartManager = cartmanager.getCartManger(request)
            cartManager.delete(**request.POST.dict())

        return HttpResponseRedirect('/cart/queryAll/')


class CartListView(View):
    def get(self,request):
        cartManager = cartmanager.getCartManger(request)
        cartList = cartManager.queryAll()
        return render(request,'cart.html',{'cartList':cartList})