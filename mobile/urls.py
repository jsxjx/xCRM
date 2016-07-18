from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns=[
   url(r'^login$', views.login, name='login'),
]
