from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns=[
   #url(r'^index$', views.index, name='index'),
   url(r'^home$', views.home, name='home'),
   url(r'^login$', views.login, name='login'),
   url(r'^logout$', views.logout, name='logout'),
   url(r'^ajax$', views.ajax, name='ajax'),
   url(r'^tile$', views.tile, name='tile'),
   url(r'^xlsoutput$', views.xlsoutput, name='xlsoutput'),
   url(r'^.*$', views.home, name='home')
]
