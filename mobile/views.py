# -*- coding: UTF-8 -*-
from django.shortcuts import render
from crm.common import *
from crm.models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from models import *
import base64, json, hashlib
from pyDes import *
from elasticsearch import Elasticsearch
import django.db.transaction
from random import *
import urllib, urllib2
import datetime
import logging

log = logging.getLogger('default')


def decrypt(text):
    try:
        # 3DES key
        key = '012345678901234567893210'
        # 3DES Initial vector
        iv = '12348765'
        # No padding
        pad = None
        # 3DES object
        des = triple_des(key, CBC, iv, pad, PAD_PKCS5)
        text = base64.decodestring(text)
        decryptStr = des.decrypt(text, pad, PAD_PKCS5)
    except Exception, e:
        decryptStr = ''
    return decryptStr


def requireDecrypt(view_func):
    def check(*args, **kwargs):
        request = args[0]
        body = request.body
        # body = decrypt(request.body)
        request.decryptedBody = body
        try:
            body = json.loads(body)
        except Exception, e:
            result = {'code': 1000,
                      'desc': u'无效的请求',
                      'data': {}
                      }
            resultStr = json.dumps(result)
            return HttpResponse(resultStr)
        try:
            return view_func(*args, **kwargs)
        except Exception, e:
            print e.message
            result = {'code': 2000,
                      'desc': '%s' % e.message,
                      'data': {}
                      }
            resultStr = json.dumps(result)
            return HttpResponse(resultStr)

    return check


def requireLoginAndDecrypt(view_func):
    def check(*args, **kwargs):
        request = args[0]
        body = request.body
        # body = decrypt(request.body)
        request.decryptedBody = body
        try:
            body = json.loads(body)
        except Exception, e:
            result = {'code': 1000,
                      'desc': u'无效的请求',
                      'data': {}
                      }
            resultStr = json.dumps(result)
            return HttpResponse(resultStr)
        userId = body.get('userId', None)
        if not userId:
            result = {'code': 1001,
                      'desc': u'未登录',
                      'data': {}
                      }
            resultStr = json.dumps(result)
            return HttpResponse(resultStr)
        if User.objects.filter(userId=userId).count() == 0:
            result = {'code': 1002,
                      'desc': u'无效用户',
                      'data': {}
                      }
            resultStr = json.dumps(result)
            return HttpResponse(resultStr)
        try:
            return view_func(*args, **kwargs)
        except Exception, e:
            print e.message
            result = {'code': 2000,
                      'desc': '%s' % e.message,
                      'data': {}
                      }
            resultStr = json.dumps(result)
            return HttpResponse(resultStr)

    return check


@csrf_exempt
def login(request):
    #
    result = {'code': 0,
              'desc': u'success',
              'data': {'userId': '%s' % '123123'}
              }
    resultStr = json.dumps(result)
    return HttpResponse(resultStr)
