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


def decrypt(text, dec=True):
    if dec:
        try:
            # 3DES key
            key = '012345678901234567890123'
            # 3DES Initial vector
            iv = '12345678'
            # No padding
            pad = None
            # 3DES object
            des = triple_des(key, CBC, iv, pad, PAD_PKCS5)
            text = base64.decodestring(text)
            decryptStr = des.decrypt(text, pad, PAD_PKCS5)
        except Exception, e:
            decryptStr = ''
        return decryptStr
    else:
        return text


def requireProcess(need_login=True, need_decrypt=True):
    def decorate(view_func):
        def check(*args, **kwargs):
            request = args[0]
            body = request.body
            if need_decrypt:
                body = decrypt(request.body, True)
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
            if need_login:
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

    return decorate


@csrf_exempt
@requireProcess(need_login=False, need_decrypt=False)
def login(request):
    body = request.decryptedBody
    body = json.loads(body)
    username = body.get('username', None)
    password = body.get('password', None)
    # Verify user
    (up, error) = verifyUser(username, password)
    # If system is in maintanence, show error
    isMaint, allowedUser = isSystemInMaintain()
    if isMaint == 'Y' and username not in allowedUser.split(';'):
        error = 'inMaint'
    if error:
        result = {'code': 1,
                  'desc': getPhraseLan('cn', 'g_default', error),
                  'data': {}
                  }
        resultStr = json.dumps(result)
        return HttpResponse(resultStr)

    result = {'code': 0,
              'desc': u'success',
              'data': {'userId': up['userloginid']}
              }
    resultStr = json.dumps(result)
    return HttpResponse(resultStr)
