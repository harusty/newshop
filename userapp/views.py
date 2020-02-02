from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
# Create your views here.
from cart.cartmanager import SessionCartManager
from userapp.models import UserInfo, Area, Address
from utils.code import *
from django.core import serializers


class RegisterView(View):
    def get(self,request):
        return render(request,'register.html')

    def post(self,requsest):
        uname = requsest.POST.get('uname','')
        pwd = requsest.POST.get('pwd','')

        userInfo = UserInfo.objects.create(uname=uname,pwd=pwd)



        if userInfo:
            requsest.session['user'] = userInfo
            return HttpResponseRedirect('/user/center')

        return HttpResponseRedirect('/user/register')


class CheckUserView(View):
    def get(self,requset):
        uname = requset.GET.get('uname',"")

        userList = UserInfo.objects.filter(uname=uname)

        flag = False
        if userList :
            flag = True
        else:
            flag = False

        return JsonResponse({'flag':flag})


class CenterView(View):
    def get(self,request):
        return render(request,'center.html')


class LogoutView(View):
    def post(self,request):
        # 删除session中的user数据
        if "user" in request.session:
            del request.session['user']

        return JsonResponse({"result":True})


class LoginView(View):
    def get(self,request):
        # 获取请求参数
        redirectUrl = request.GET.get('redirect','')
        if  redirectUrl.strip() :
            print("redirectUrl==="+redirectUrl)
            return  render(request,'login.html',{'redirect':redirectUrl})


        return  render(request,'login.html')

    def post(self,request):
        uname = request.POST.get('uname','')
        pwd = request.POST.get('pwd','')


        userInfoList = UserInfo.objects.filter(uname=uname,pwd=pwd)


        if userInfoList:
            redirectUrl = request.POST.get('redirect', '')
            request.session['user'] = userInfoList[0]
            print('loginpost===' + redirectUrl)
            # 移动session数据
            if redirectUrl == 'cart':
                sessionCartManager = SessionCartManager(request.session)
                sessionCartManager.migrateSession2DB()
                print(redirectUrl)
                return HttpResponseRedirect('/cart/queryAll')
            elif redirectUrl == 'order':
                return HttpResponseRedirect('/order/order.html?cartitems='+request.POST.get('cartitems',''))

        else :
            return HttpResponseRedirect('/user/login')

        return HttpResponseRedirect('/user/center')



class LoadCodeView(View):
    def get(self,request):
        img,code = gene_code()
        request.session['code'] = code
        return HttpResponse(img,content_type='image/png')


class CheckCodeView(View):
    def get(self,request):
        sessionCode = request.session.get('code',None)
        code = request.GET.get('code','')
        flag = code==sessionCode

        return JsonResponse({
            'flag':flag
        })


class AddressView(View):
    def get(self,request):
        userInfo = request.session.get('user', '')
        addrList = Address.objects.filter(userinfo=userInfo)
        return render(request, 'address.html', {'addresslist': addrList})

    def post(self,request):
        aname = request.POST.get('aname','')
        aphone = request.POST.get('aphone','')
        addr = request.POST.get('addr','')
        userInfo = request.session.get('user','')

        addInfo = Address.objects.create(aname=aname,aphone=aphone,addr=addr,is_default= (lambda count:True if count==0 else False)(userInfo.address_set.all().count()),userinfo=userInfo)

        addrList = Address.objects.filter(userinfo=userInfo)

        return render(request,'address.html',{'addresslist':addrList})

        return HttpResponse('hello address')




class LoadAreaView(View):
    def get(self,request):
        pid = request.GET.get('pid',-1)
        pid = int(pid)
        areaList = Area.objects.filter(parentid=pid)
        areaList = serializers.serialize('json',areaList)
        return JsonResponse({'arealist':areaList})

