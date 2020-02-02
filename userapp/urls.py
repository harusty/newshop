from django.conf.urls import url

from userapp import views

urlpatterns=[
    url(r'^register/$',views.RegisterView.as_view()),
    url(r'^checkUname/$',views.CheckUserView.as_view()),
    url(r'^center/$',views.CenterView.as_view()),
    url(r'^logout/$',views.LogoutView.as_view()),
    url(r'^login/$',views.LoginView.as_view()),
    url(r'^loadcode/$',views.LoadCodeView.as_view()),
    url(r'^loadcode.jpg$',views.LoadCodeView.as_view()),
    url(r'^checkcode/$',views.CheckCodeView.as_view()),
    url(r'^address/$',views.AddressView.as_view()),
    url(r'^loadArea/$',views.LoadAreaView.as_view()),
]
