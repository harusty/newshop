#encoding=utf-8
from django.conf.urls import url

from good import views

urlpatterns=[
    url(r'^$',views.IndexView.as_view()),
    url(r'^category/(\d+)$',views.IndexView.as_view()),
    url(r'^category/(\d+)/page/(\d+)$',views.IndexView.as_view()),
    url(r'^goodsdetails/(\d+)$', views.GoodsDetailsView.as_view()),
]