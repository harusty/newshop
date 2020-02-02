#coding=utf-8

from django.conf.urls import url
from cart import views

urlpatterns=[
    url(r'^$',views.AddCartView.as_view()),
    url(r'^queryAll/$',views.CartListView.as_view()),
]