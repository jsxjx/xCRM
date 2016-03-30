# -*- coding: UTF-8 -*-
# Common class and functions
# Import Django Models
import os
import hashlib
import base64
import xlwt
import pytz
import json
import logging
import time
import datetime
import traceback
import collections
import pickle

from models import *
from django.db.models import Q
from django.utils import timezone
from django.db import transaction
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseNotFound
from django.template import RequestContext, loader
from django.views import generic
from django import forms
from django.db.models import Count, Sum
from django.views.decorators.csrf import csrf_exempt

from django.core import serializers
from django.core.cache import cache

from random import *
from django.template import Template
from django.db import connection, transaction
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from django.db.models.fields.files import ImageFieldFile
from django.db.models.fields.files import FieldFile

log = logging.getLogger('default')
log.info('common.py initialized')
phrase_cache = None
log.info('phrase_cache initialized %s' % phrase_cache)

html_separator = """<div class="clearfix" style="height:2px"></div>"""
# Common Order Context
coCtxName = 'co'
# Common Bp Context
cbCtxName = 'cb'
appCtxName = 'app'


# File upload form
class FileUploadForm(forms.Form):
    file = forms.FileField()
    description = forms.CharField(required=False)
    version = forms.CharField(required=False)


# Select option class, represent for single field selection
class SelectOption(object):
    def __init__(self, field, opt='eq', low='', high=''):
        self.field = field
        self.opt = opt
        self.low = low
        self.high = high


# Selection map/dictionary
class SelectOptionMap(object):
    def __init__(self):
        # self.__map = {}
        self.__fieldNameList = []
        self.__list = []

    def addSelectOption(self, selectOption):
        self.__fieldNameList.append(selectOption.field)
        self.__list.append(selectOption)

    def getSelectOptionAtIndex(self, idx):
        return self.__list[idx]

    def setSelectOptionAtIndex(self, idx, selectOption):
        self.__fieldNameList[idx] = selectOption.field
        self.__list[idx] = selectOption

    def removeSelectOptionAtIndex(self, idx):
        # Remove search criteria by index
        del self.__list[idx]
        del self.__fieldNameList[idx]

    def removeAll(self):
        self.__list = []
        self.__fieldNameList = []

    def clearValue(self):
        for selectOption in self.__list:
            if selectOption.field != 'type':
                selectOption.low = ''
                selectOption.high = ''

    def getSelectOption(self, field):
        return self.getMap().get(field, None)

    def getMap(self):
        map = {}
        for selectOption in self.__list:
            options = map.get(selectOption.field, None)
            if not options:
                options = []
                map[selectOption.field] = options
            options.append(selectOption)
        return map

    def getFieldNameList(self):
        fl = self.__fieldNameList[:]
        return fl

    def getList(self):
        l = self.__list[:]
        return l


# Base application context
class AppContext(object):
    def __init__(self):
        self.status = None
        self.messagebar = []


# CommonOrder application context
class CommonOrderContext(object):
    def __init__(self):
        # Order search form
        self.searchBean = SelectOptionMap()
        # Order type selected
        self.orderType = None
        # Order id selected
        self.orderId = None
        # Saved search names
        self.savedName = None
        # Result ids
        self.reids = None
        # For records store in session
        self.resultHeaders = None
        self.resultItems = None
        # For new order creation
        self.currentOrder = None
        # For mode, 'search', 'edit', 'new', 'detail'
        self.mode = None
        # Change log model
        self.changeLog = None
        # field errors
        # store as {'fieldkey':'error string'}, e.g. {'description':'should not be null'}
        self.fieldErrors = None
        # Attachments
        self.attachments = None


# CommonBp application context
class CommonBpContext(object):
    def __init__(self):
        # Bp search form
        self.searchBean = SelectOptionMap()
        # Bp type selected
        self.bpType = None
        # Bp id selected
        self.bpId = None
        # Saved search names
        self.savedName = None
        # Result ids
        self.reids = None
        # For records store in session
        self.resultHeaders = None
        self.resultItems = None
        # For new bp creation
        self.currentBp = None
        # For mode, 'search', 'edit', 'new', 'detail'
        self.mode = None
        # Change log model
        self.changeLog = None
        # field errors
        # store as {'fieldkey':'error string'}, e.g. {'description':'should not be null'}
        self.fieldErrors = None
        # Attachments
        self.attachments = None


class StepViewContext(object):
    def __init__(self):
        self.selectedOrderId = None
        self.myOrders = None
        self.selectedOrder = None


# Get context from session by name
def getContext(request, name):
    data = request.session.get(name, None)
    if data:
        obj = pickle.loads(data)
        return obj
    return None


# Set context in to session with name
# pickle is used to serialize context instance
def setContext(request, name, ctx):
    data = pickle.dumps(ctx)
    request.session[name] = data


class StdView(object):
    def __init__(self, page=None):
        self.page = page

    def initialize(self, request, context):
        log.info('Initialized')

    def search(self, request, context):
        log.info('onSearch')

    def view(self, request, context):
        log.info('onView')

    def new(self, request, context):
        log.info('onNew')

    def edit(self, request, context):
        log.info('onEdit')

    def save(self, request, context):
        log.info('onSave')

    def cancel(self, request, context):
        log.info('onCancel')

    def back(self, request, context):
        log.info('onBack')

    def xlsoutput(self, request, context):
        log.info('onXLSoutput')


# This class is base view class for order and bp
class ModelStdView(object):
    def __init__(self, page=None):
        self.page = page

    def initializeMessageBar(self, request, context):
        mb = context.get('messagebar', None)
        if not mb:
            context['messagebar'] = []

    def initialize(self, request, context):
        log.info('Initialized')
        # Set search status
        context['nav']['pageStatus'] = 'search'
        self.initializeMessageBar(request, context)
        pass

    def search(self, request, context):
        log.info('onSearch')
        context['nav']['pageStatus'] = 'search'
        self.initializeMessageBar(request, context)
        pass

    def view(self, request, context):
        log.info('onView')
        context['nav']['pageStatus'] = 'detail'
        self.initializeMessageBar(request, context)
        pass

    def new(self, request, context):
        log.info('onNew')
        context['nav']['pageStatus'] = 'new'
        self.initializeMessageBar(request, context)
        pass

    def edit(self, request, context):
        log.info('onEdit')
        context['nav']['pageStatus'] = 'edit'
        self.initializeMessageBar(request, context)
        pass

    def save(self, request, context):
        log.info('onSave')
        context['nav']['pageStatus'] = 'detail'
        self.initializeMessageBar(request, context)
        pass

    def cancel(self, request, context):
        log.info('onCancel')
        context['nav']['pageStatus'] = 'detail'
        self.initializeMessageBar(request, context)
        pass

    def back(self, request, context):
        log.info('onBack')
        context['nav']['pageStatus'] = 'search'
        self.initializeMessageBar(request, context)

    def upload(self, request, context):
        context['nav']['pageStatus'] = 'edit'
        self.initializeMessageBar(request, context)

    def deletefile(self, request, context):
        context['nav']['pageStatus'] = 'edit'
        self.initializeMessageBar(request, context)

    def xlsoutput(self, request, context):
        log.info('onXLSoutput')
        self.initializeMessageBar(request, context)
        pass


#
# Below 2 view classes is similar and important. Be careful when doing any change on them.
# The view will read fields configuration from database table, generate the view/edit layout
# with UtilTag buildFields (buildXXXX etc)
# The target is to maximum the python dynamic feature and reduce unecessary/redundant coding.
# When adding new fields for an order or BP, you can just:
# 1. Add fields in models.py for a table -> makemigrations -> migrate
# 2. Config the field in table StdViewLayoutConf/BPStdViewLayoutConf
#
# If you are not able to understand -> It's your fault, try Ctrl+A and Delete
# to easy your lift. Enjoy!
#
# This view class provide general feature for viewing/editing an order
class CommonOrderAppView(ModelStdView):
    def __init__(self, page=None):
        ModelStdView.__init__(self, page)

    def initialize(self, request, context):
        super(CommonOrderAppView, self).initialize(request, context)
        coContext = CommonOrderContext()
        coContext.searchBean.addSelectOption(SelectOption('type', low='SA01'))
        coContext.searchBean.addSelectOption(SelectOption('description'))
        coContext.searchBean.addSelectOption(SelectOption('empResp', low=getCurrentUserBp(request).id))
        coContext.searchBean.addSelectOption(SelectOption('stage'))
        coContext.searchBean.addSelectOption(SelectOption('district'))
        coContext.searchBean.addSelectOption(SelectOption('channel'))
        coContext.searchBean.addSelectOption(SelectOption('travelAmount'))
        coContext.mode = 'search'
        setContext(request, coCtxName, coContext)

    def search(self, request, context):
        super(CommonOrderAppView, self).search(request, context)
        coContext = getContext(request, coCtxName)
        mode = request.POST.get('pageParams', None)
        if mode == 'cradd':
            # Add a criteria
            coContext.searchBean.addSelectOption(SelectOption('description'))
            setContext(request, coCtxName, coContext)
        elif mode == 'crrmv':
            # Remove a criteria
            searchList = coContext.searchBean.getList()
            co = request.session.get('co', None)
            if len(searchList) > 3:
                coContext.searchBean.removeSelectOptionAtIndex(len(searchList) - 1)
                setContext(request, coCtxName, coContext)
        elif mode == 'crcls':
            # Clear low and high value
            coContext.searchBean.clearValue()
            setContext(request, coCtxName, coContext)
        elif mode == 'crchg':
            # For field name / operator / value changing
            modifySearchBeanFromFormData(request, coContext.searchBean)
            typeOpts = coContext.searchBean.getSelectOption('type')
            if len(typeOpts) == 1:
                coContext.orderType = typeOpts[0].low
            setContext(request, coCtxName, coContext)
        elif mode == 'back':
            pass
        elif mode == 'crsav':
            # Save user search criteria
            saveName = request.POST.get('saveAs')
            if saveName:
                uid = request.session['up']['userloginid']
                userLogin = UserLogin.objects.get(id=uid)
                modifySearchBeanFromFormData(request, coContext.searchBean)
                # Delete existing savedName
                UserSavedSearchFavorite.objects.filter(userlogin=userLogin, type='commonOrder', name=saveName).delete()
                searchList = coContext.searchBean.getList()
                for i in range(len(searchList)):
                    selectOption = searchList[i]
                    uf = UserSavedSearchFavorite()
                    uf.userlogin = userLogin
                    uf.type = 'commonOrder'
                    uf.name = saveName
                    uf.sortOrder = i
                    uf.property = selectOption.field
                    uf.operation = selectOption.opt
                    uf.low = selectOption.low
                    uf.high = selectOption.high
                    uf.save()
        elif mode == 'csrmv':
            uid = request.session['up']['userloginid']
            userLogin = UserLogin.objects.get(id=uid)
            savedName = request.POST.get('savedName', None)
            if savedName:
                # Remove user saved criteria
                UserSavedSearchFavorite.objects.filter(userlogin=userLogin, type='commonOrder', name=savedName).delete()
        else:
            # Start search process
            # Check whether user called saved search
            savedName = request.POST.get('savedName', None)
            otype = None
            # If saved search, read criteria from database
            if mode == 'savsf':
                if savedName:
                    coContext.savedName = savedName
                    uid = request.session['up']['userloginid']
                    userLogin = UserLogin.objects.get(id=uid)
                    coContext.searchBean.removeAll()
                    for saved in UserSavedSearchFavorite.objects.filter(userlogin=userLogin, type='commonOrder',
                                                                        name=savedName).all():
                        coContext.searchBean.addSelectOption(
                            SelectOption(saved.property, saved.operation, saved.low, saved.high))
                else:
                    coContext.savedName = ''
            else:
                # Build search criteria list
                modifySearchBeanFromFormData(request, coContext.searchBean)

            # Remember the order type if only 1 value is given
            types = coContext.searchBean.getSelectOption('type')
            if len(types) == 1:
                coContext.orderType = types[0].low
                fieldsOfOrder = OrderFieldDef.objects.filter(
                    Q(orderType=coContext.orderType))  # ~Q(attributeType='Addon'
            else:
                coContext.orderType = None
            # Search order by criteria list
            filter = {}
            q = Q()
            orders = Order.objects.all()
            conditions = coContext.searchBean.getMap()
            for k, v in conditions.items():
                if k in ['id', 'type', 'description', 'createdAt', 'createdBy', 'updatedAt', 'updatedBy', 'status',
                         'priority']:
                    if len(v) == 1:
                        # Only one condition, AND
                        opt = v[0].opt
                        low = v[0].low
                        high = v[0].high
                        buildQobject(q, k, opt, low, high, Q.AND)
                    else:
                        qor = Q()
                        for c in v:
                            opt = c.opt
                            low = c.low
                            high = c.high
                            buildQobject(qor, k, opt, low, high, Q.OR)
                        q.add(qor, Q.AND)
                else:
                    # The field is not in columns of Order
                    # It could be user customized or other criteria
                    # fieldsOfOrder must not be empty since oder type is given
                    if not fieldsOfOrder:
                        # Should not happen
                        continue
                    f = fieldsOfOrder.filter(fieldKey=k)
                    if f:
                        if f[0].attributeType == 'Addon':
                            if f[0].fieldKey == 'district':
                                innerQ = Q()
                                if len(v) == 1:
                                    opt = v[0].opt
                                    low = v[0].low
                                    high = v[0].high
                                    if not low and not high:
                                        continue
                                    newQ = Q()
                                    newQ.add(Q(**{'orderpf__pf__key': '00001'}), newQ.AND)
                                    newQ.add(Q(**{'orderpf__bp__address1__district': low}), newQ.AND)
                                    if opt == 'eq':
                                        innerQ.add(newQ, q.AND)
                                    elif opt == 'ne':
                                        innerQ.add(~newQ, q.AND)
                                else:
                                    newQ = Q()
                                    for c in v:
                                        opt = c.opt
                                        low = c.low
                                        high = c.high
                                        if not low and not high:
                                            continue
                                        subQ = Q()
                                        subQ.add(Q(**{'orderpf__pf__key': '00001'}), subQ.AND)
                                        subQ.add(Q(**{'orderpf__bp__address1__district': low}), subQ.AND)
                                        if opt == 'eq':
                                            newQ.add(subQ, q.OR)
                                        elif opt == 'ne':
                                            newQ.add(~subQ, q.OR)
                                    innerQ.add(newQ, newQ.AND)
                                orders = orders.filter(innerQ)
                        elif f[0].storeType == 'PF':
                            # Let's say only support eq ad ne
                            innerQ = Q()
                            if len(v) == 1:
                                opt = v[0].opt
                                low = v[0].low
                                high = v[0].high
                                if not low and not high:
                                    continue
                                newQ = Q()
                                newQ.add(Q(**{'orderpf__pf__key': f[0].storeKey}), newQ.AND)
                                newQ.add(Q(**{'orderpf__bp__id': low}), newQ.AND)
                                if opt == 'eq':
                                    innerQ.add(newQ, q.AND)
                                elif opt == 'ne':
                                    innerQ.add(~newQ, q.AND)
                            else:
                                newQ = Q()
                                for c in v:
                                    opt = c.opt
                                    low = c.low
                                    high = c.high
                                    if not low and not high:
                                        continue
                                    subQ = Q()
                                    subQ.add(Q(**{'orderpf__pf__key': f[0].storeKey}), subQ.AND)
                                    subQ.add(Q(**{'orderpf__bp__id': low}), subQ.AND)
                                    if opt == 'eq':
                                        newQ.add(subQ, q.OR)
                                    elif opt == 'ne':
                                        newQ.add(~subQ, q.OR)
                                innerQ.add(newQ, newQ.AND)
                            orders = orders.filter(innerQ)
                        elif f[0].storeType == 'Customized':
                            newKey = ''.join(['ordercustomized__', k])
                            if len(v) == 1:
                                # Only one condition, AND
                                opt = v[0].opt
                                low = v[0].low
                                high = v[0].high
                                if not low and not high:
                                    continue
                                buildQobject(q, newKey, opt, low, high, Q.AND)
                            else:
                                qor = Q()
                                for c in v:
                                    opt = c.opt
                                    low = c.low
                                    high = c.high
                                    if not low and not high:
                                        continue
                                    buildQobject(qor, newKey, opt, low, high, Q.OR)
                                q.add(qor, Q.AND)
            if q:
                # modelIds = Order.objects.filter(q).values('id')
                modelIds = orders.filter(q).values('id')
            else:
                # modelIds = Order.objects.values('id')
                modelIds = orders.values('id')
            coContext.reids = [m['id'] for m in modelIds]
            setContext(request, coCtxName, coContext)

    def view(self, request, context):
        super(CommonOrderAppView, self).view(request, context)
        coContext = getContext(request, coCtxName)
        if not coContext:
            # Create context, since 'view' can be accessed directly
            coContext = CommonOrderContext()
            setContext(request, coCtxName, coContext)
        commonOrderId = context['nav'].get('pageParams', None)
        if commonOrderId:
            coContext.orderId = commonOrderId
        coContext.orderType = Order.objects.get(id=coContext.orderId).type.key
        coContext.mode = 'detail'
        model = self.loadCommonOrder(coContext.orderId, request, context)
        be = getBusinessEntity(coContext.orderType, model, request)
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        be.setCurrentUser(userBp)
        context['commonOrderTitle'] = "%s %s %s" % (
            be.orderModel.type.description,
            be.orderModel.id, be.orderModel.description)
        coContext.currentOrder = be
        changeLog = ChangeHistory.objects.filter(objectId=coContext.orderId, type='Order').order_by('-updatedAt')
        coContext.changeLog = changeLog
        # attachments = OrderFileAttachment.objects.filter(order__id=coContext.orderId).order_by('-createdAt')
        # coContext.attachments = attachments
        setContext(request, coCtxName, coContext)
        AddObjectIdToHistory(request, context, coContext.orderId, 'Order')

    def edit(self, request, context):
        coContext = getContext(request, coCtxName)
        coContext.fieldErrors = {}
        if not coContext.currentOrder:
            if coContext.orderId:
                model = self.loadCommonOrder(coContext.orderId, request, context)
                be = getBusinessEntity(coContext.orderType, model, request)
                coContext.currentOrder = be
        context['commonOrderTitle'] = "%s %s %s" % (
            coContext.currentOrder.orderModel.type.description,
            coContext.currentOrder.orderModel.id, coContext.currentOrder.orderModel.description)
        # Check user authorization for editing
        authName = 'Order_%s_Access' % coContext.orderType
        (_, _, canEdit, _) = getUserAuthorization(context, authName)
        if not canEdit:
            # Return to view page if not authorized
            self.view(request, context)
            return
        uid = request.session['up']['userloginid']
        userLogin = UserLogin.objects.get(id=uid)
        # Check lock and add lock
        lock = GetEntityLock(coContext.orderId, 'Order', userLogin.userbp.id)
        if lock:
            self.initializeMessageBar(request, context)
            lockedByName = BP.objects.get(id=lock.lockedBy).displayName()
            lockInfo = u'该记录正在被 %s 编辑' % lockedByName
            context['messagebar'].extend([{'type': 'error',
                                           'content': lockInfo}])
            context['nav']['pageStatus'] = 'detail'
            return
        AddEntityLock(coContext.orderId, 'Order', userLogin.userbp.id)
        coContext.mode = 'edit'
        setContext(request, coCtxName, coContext)
        super(CommonOrderAppView, self).edit(request, context)

    def new(self, request, context):
        # User clicked new button
        # Create a default Order model and wrap as Business Entity by its type
        # Save this entity in session
        super(CommonOrderAppView, self).new(request, context)
        # Get Order Type from pageParams
        orderType = request.POST.get('pageParams', None)
        coContext = getContext(request, coCtxName)
        coContext.orderType = orderType
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        # Create new Order
        model = Order()
        model.type = OrderType.objects.get(key=orderType)
        model.createdBy = userBp
        # Initialize default value
        model.priority = PriorityType.objects.get(id=1)
        model.status = StatusType.objects.get(id=1)
        model.updatedBy = userBp
        model.ordercustomized = OrderCustomized()
        model.activity = Activity()
        # Wrap as Business Entity
        be = getBusinessEntity(orderType, model, request)
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        be.setCurrentUser(userBp)
        coContext.currentOrder = be
        # Clear order id in context
        coContext.orderId = None
        # Save in session and set mode to new
        be.pageStatus = coContext.mode = 'new'
        setContext(request, coCtxName, coContext)

    def save(self, request, context):
        # Save an order
        super(CommonOrderAppView, self).save(request, context)
        context['messagebar'] = []
        errors = []
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        coContext = getContext(request, coCtxName)
        coContext.fieldErrors = {}
        try:
            be = coContext.currentOrder
            # Start transaction
            with transaction.atomic():
                be.setCurrentUser(userBp)
                be.pageStatus = coContext.mode
                # if be.pageStatus == 'new':
                # If mode is new, means it's may not be saved, save it
                # Save ordercustomized since usually it's needed
                be.orderModel.save()
                be.orderModel.ordercustomized.order = be.orderModel
                be.orderModel.ordercustomized.save()
                be.orderModel.save()
                fieldsOfOrder = OrderFieldDef.objects.filter(Q(orderType=be.orderModel.type), ~Q(attributeType='Addon'))
                configuredFields = StdViewLayoutConf.objects.filter(field__in=fieldsOfOrder, visibility=True,
                                                                    viewType__key='Detail', valid=True).order_by(
                    'locRow', 'locCol')
                changeLog = []
                for cf in configuredFields:
                    confData = GetFieldConfigData(be, cf)
                    # Get field phrase
                    phraseId = cf.labelPhraseId
                    if not phraseId:
                        phraseId = cf.field.fieldKey
                    fieldname = getPhrase(request, 'order', phraseId)
                    # Ignore id field, it's not changable
                    if cf.field.fieldKey == 'id':
                        continue
                    fieldValue = request.POST.get(cf.field.fieldKey, None)

                    if not confData['editable']:
                        continue
                    # Call get method
                    try:
                        oldKeyValue, oldDisplayValue = GetFieldValue(be, **confData)
                        if confData['fieldType'] == 'MI':
                            oldDisplayValue = ','.join(
                                ['%s %s' % (v['charValue1'], v['charValue2']) for v in oldDisplayValue])
                        SetFieldValue(be, fieldValue, **confData)
                        newKeyValue, newDisplayValue = GetFieldValue(be, **confData)
                        if confData['fieldType'] == 'MI':
                            newDisplayValue = ','.join(
                                ['%s %s' % (v['charValue1'], v['charValue2']) for v in newDisplayValue])
                    except Exception, e:
                        coContext.fieldErrors[confData['fieldKey']] = "%s %s" % (fieldname, e.message)
                    if str(oldKeyValue) != str(newKeyValue) or str(oldDisplayValue) != str(newDisplayValue):
                        oh = ChangeHistory()
                        oh.objectId = be.orderModel.id
                        oh.type = 'Order'
                        oh.objectField = confData['fieldKey']
                        oh.newValue = newDisplayValue
                        oh.newKeyValue = newKeyValue
                        oh.oldValue = oldDisplayValue
                        oh.oldKeyValue = oldKeyValue
                        oh.updatedBy = userBp.id
                        oh.updatedAt = datetime.datetime.now()
                        changeLog.append(oh)
                be.save()
                if len(coContext.fieldErrors) > 0:
                    raise Exception("Error")
                for changelog in changeLog:
                    changelog.save()
            coContext.orderId = be.orderModel.id
        except Exception, e:
            for key, error in coContext.fieldErrors.items():
                errors.extend([{'type': 'error', 'content': error}])
            errors.extend([{'type': 'error', 'content': e.message}])

        # Save errors/info in context
        context['messagebar'].extend(errors)
        errs = [x for x in errors if x['type'] == 'error']
        if len(errs) == 0:
            context['messagebar'].extend([{'type': 'success',
                                           'content': getPhrase(request, 'g_default', 'orderSaved', u"数据已保存")}])
            coContext.mode = 'detail'
            DeleteEntityLock(coContext.orderId, 'Order', userBp.id)
            setContext(request, coCtxName, coContext)
            navPath = request.session.get('navPath', None)
            if len(navPath) > 2:
                del navPath[-2:]
            self.view(request, context)
        else:
            coContext.mode = 'edit'
            setContext(request, coCtxName, coContext)
            super(CommonOrderAppView, self).edit(request, context)
            navPath = request.session.get('navPath', None)
            if len(navPath) > 1:
                del navPath[-1:]

    def cancel(self, request, context):
        coContext = getContext(request, coCtxName)
        if coContext is None:
            self.initialize(request, context)
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        DeleteEntityLock(coContext.orderId, 'Order', userBp.id)
        if coContext.currentOrder and coContext.mode != 'new':
            coContext.mode = 'detail'
            setContext(request, coCtxName, coContext)
            context['commonOrderTitle'] = "%s %s %s" % (
                coContext.currentOrder.orderModel.type.description,
                coContext.currentOrder.orderModel.id, coContext.currentOrder.orderModel.description)
            super(CommonOrderAppView, self).cancel(request, context)
        else:
            self.initialize(request, context)

    def back(self, request, context):
        super(CommonOrderAppView, self).back(request, context)
        return self.page

    def upload(self, request, context):
        fuf = FileUploadForm(request.POST, request.FILES)

        if fuf.is_valid():
            coContext = getContext(request, coCtxName)
            upfile = fuf.cleaned_data['file']
            fa = OrderFileAttachment()
            fa.order = coContext.currentOrder.orderModel
            fa.file = upfile
            fa.description = upfile.name
            fa.actualfilename = upfile.name
            fa.name = upfile.name
            userBp = getCurrentUserBp(request)
            fa.createdBy = userBp
            fa.save()
        super(CommonOrderAppView, self).upload(request, context)

    def deletefile(self, request, context):
        fileId = context['nav']['pageParams']
        ofa = OrderFileAttachment.objects.get(id=fileId)
        ofa.deleteFlag = True
        ofa.save()
        super(CommonOrderAppView, self).deletefile(request, context)

    def download(self, request, context):
        fileId = context['nav']['pageParams']
        fa = OrderFileAttachment.objects.get(id=fileId)
        filename = fa.actualfilename
        data = fa.file._get_file().read()
        clientSystem = request.META['HTTP_USER_AGENT']
        if clientSystem.find('Windows') > -1:
            filename = filename.encode('cp936')
        else:
            filename = filename.encode('utf-8')
        response = HttpResponse(data, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    def leave(self, request, context):
        coContext = getContext(request, coCtxName)
        if coContext:
            uid = request.session['up']['userloginid']
            userBp = UserLogin.objects.get(id=uid).userbp
            DeleteEntityLock(coContext.orderId, 'Order', userBp.id)

    def xlsoutput(self, request, context):
        coContext = getContext(request, coCtxName)
        return getCommonOrderXLS(request, coContext.resultHeaders, coContext.resultItems)

    def createFollowUp(self, request, context):
        # User clicked new button
        # Create a default Order model and wrap as Business Entity by its type
        # Save this entity in session
        super(CommonOrderAppView, self).new(request, context)
        # Get orginal order id
        previousOrderId = request.POST.get('pageParams', None)
        # Get Order Type from pageMode
        orderType = request.POST.get('pageMode', None)
        coContext = getContext(request, coCtxName)
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        DeleteEntityLock(previousOrderId, 'Order', userBp.id)
        coContext.orderType = orderType
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        # Create new Order
        model = Order()
        model.type = OrderType.objects.get(key=orderType)
        model.createdBy = userBp
        # Initialize default value
        model.priority = PriorityType.objects.get(id=1)
        model.status = StatusType.objects.get(id=1)
        model.updatedBy = userBp
        model.ordercustomized = OrderCustomized()
        model.activity = Activity()
        # Wrap as Business Entity
        be = getBusinessEntity(orderType, model, request)
        be.setPreviousOrderModel(Order.objects.get(id=previousOrderId))
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        be.setCurrentUser(userBp)
        coContext.currentOrder = be
        # Clear order id in context
        coContext.orderId = None
        # Save in session and set mode to new
        be.pageStatus = coContext.mode = 'new'
        setContext(request, coCtxName, coContext)

    def loadCommonOrder(self, commonOrderId, request, context):
        model = Order.objects.get(id=commonOrderId)
        mb = context.get('messagebar', None)
        if not mb:
            mb = context['messagebar'] = []
        return model


# This view class provide general feature for viewing/editing an BP
class CommonBpAppView(ModelStdView):
    def __init__(self, page=None):
        ModelStdView.__init__(self, page)

    def initialize(self, request, context):
        super(CommonBpAppView, self).initialize(request, context)
        cbContext = CommonBpContext()
        cbContext.searchBean.addSelectOption(SelectOption('type', low=''))
        cbContext.searchBean.addSelectOption(SelectOption('firstName'))
        cbContext.searchBean.addSelectOption(SelectOption('middleName'))
        cbContext.searchBean.addSelectOption(SelectOption('lastName'))
        cbContext.searchBean.addSelectOption(SelectOption('name1'))
        cbContext.searchBean.addSelectOption(SelectOption('name2'))
        cbContext.mode = 'search'
        setContext(request, cbCtxName, cbContext)

    def search(self, request, context):
        super(CommonBpAppView, self).search(request, context)
        cbContext = getContext(request, cbCtxName)
        mode = request.POST.get('pageParams', None)
        if mode == 'cradd':
            # Add a criteria
            cbContext.searchBean.addSelectOption(SelectOption('name1'))
            setContext(request, cbCtxName, cbContext)
        elif mode == 'crrmv':
            # Remove a criteria
            searchList = cbContext.searchBean.getList()
            if len(searchList) > 3:
                cbContext.searchBean.removeSelectOptionAtIndex(len(searchList) - 1)
                setContext(request, cbCtxName, cbContext)
        elif mode == 'crcls':
            # Clear low and high value
            cbContext.searchBean.clearValue()
            setContext(request, cbCtxName, cbContext)
        elif mode == 'crchg':
            # For field name / operator / value changing
            modifySearchBeanFromFormData(request, cbContext.searchBean)
            typeOpts = cbContext.searchBean.getSelectOption('type')
            if len(typeOpts) == 1:
                cbContext.bpType = typeOpts[0].low
            setContext(request, cbCtxName, cbContext)
        elif mode == 'back':
            pass
        elif mode == 'crsav':
            # Save user search criteria
            saveName = request.POST.get('saveAs')
            if saveName:
                uid = request.session['up']['userloginid']
                userLogin = UserLogin.objects.get(id=uid)
                modifySearchBeanFromFormData(request, cbContext.searchBean)
                # Delete existing savedName
                UserSavedSearchFavorite.objects.filter(userlogin=userLogin, type='commonBp',
                                                       name=saveName).delete()
                searchList = cbContext.searchBean.getList()
                for i in range(len(searchList)):
                    selectOption = searchList[i]
                    uf = UserSavedSearchFavorite()
                    uf.userlogin = userLogin
                    uf.type = 'commonBp'
                    uf.name = saveName
                    uf.sortOrder = i
                    uf.property = selectOption.field
                    uf.operation = selectOption.opt
                    uf.low = selectOption.low
                    uf.high = selectOption.high
                    uf.save()
        elif mode == 'csrmv':
            uid = request.session['up']['userloginid']
            userLogin = UserLogin.objects.get(id=uid)
            savedName = request.POST.get('savedName', None)
            if savedName:
                # Remove user saved criteria
                UserSavedSearchFavorite.objects.filter(userlogin=userLogin, type='commonOrder',
                                                       name=savedName).delete()
        else:
            # Start search process
            # Check whether user called saved search
            savedName = request.POST.get('savedName', None)
            # If saved search, read criteria from database
            if mode == 'savsf':
                if savedName:
                    cbContext.savedName = savedName
                    uid = request.session['up']['userloginid']
                    userLogin = UserLogin.objects.get(id=uid)
                    cbContext.searchBean.removeAll()
                    for saved in UserSavedSearchFavorite.objects.filter(userlogin=userLogin, type='commonBp',
                                                                        name=savedName).all():
                        cbContext.searchBean.addSelectOption(
                            SelectOption(saved.property, saved.operation, saved.low, saved.high))
                else:
                    cbContext.savedName = ''
            else:
                # Build search criteria list
                modifySearchBeanFromFormData(request, cbContext.searchBean)

            # Remember the order type if only 1 value is given
            types = cbContext.searchBean.getSelectOption('type')
            if len(types) == 1:
                cbContext.bpType = types[0].low
                fieldsOfOrder = BPFieldDef.objects.filter(
                    Q(bpType=cbContext.bpType))  # ~Q(attributeType='Addon'
            else:
                cbContext.bpType = None
            # Search order by criteria list
            filter = {}
            q = Q()
            conditions = cbContext.searchBean.getMap()
            for k, v in conditions.items():
                if k in ['id', 'type', 'firstName', 'middleName', 'lastName', 'name1', 'name2']:
                    if len(v) == 1:
                        # Only one condition, AND
                        opt = v[0].opt
                        low = v[0].low
                        high = v[0].high
                        buildQobject(q, k, opt, low, high, Q.AND)
                    else:
                        qor = Q()
                        for c in v:
                            opt = c.opt
                            low = c.low
                            high = c.high
                            buildQobject(qor, k, opt, low, high, Q.OR)
                        q.add(qor, Q.AND)
                else:
                    # The field is not in columns of Order
                    # It could be user customized or other criteria
                    # fieldsOfOrder must not be empty since oder type is given
                    if not fieldsOfOrder:
                        # Should not happen
                        continue
                    f = fieldsOfOrder.filter(fieldKey=k)
                    if f:
                        if f[0].attributeType == 'Addon':
                            pass
                        elif f[0].storeType == 'PF':
                            pass
                        elif f[0].storeType == 'Customized':
                            newKey = ''.join(['bpcustomized__', k])
                            if len(v) == 1:
                                # Only one condition, AND
                                opt = v[0].opt
                                low = v[0].low
                                high = v[0].high
                                if not low and not high:
                                    continue
                                buildQobject(q, newKey, opt, low, high, Q.AND)
                            else:
                                qor = Q()
                                for c in v:
                                    opt = c.opt
                                    low = c.low
                                    high = c.high
                                    if not low and not high:
                                        continue
                                    buildQobject(qor, newKey, opt, low, high, Q.OR)
                                q.add(qor, Q.AND)
            if q:
                modelIds = BP.objects.filter(q).values('id')
            else:
                modelIds = BP.objects.values('id')
            cbContext.reids = [m['id'] for m in modelIds]
            setContext(request, cbCtxName, cbContext)

    def view(self, request, context):
        super(CommonBpAppView, self).view(request, context)
        cbContext = getContext(request, cbCtxName)
        if not cbContext:
            # Create context, since 'view' can be accessed directly
            cbContext = CommonBpContext()
            setContext(request, cbCtxName, cbContext)
        commonBpId = context['nav'].get('pageParams', None)
        if commonBpId:
            cbContext.bpId = commonBpId
        cbContext.bpType = BP.objects.get(id=cbContext.bpId).type.key
        cbContext.mode = 'detail'
        model = self.loadCommonBp(cbContext.bpId, request, context)
        be = getBusinessPartnerEntity(cbContext.bpType, model, request)
        context['commonBpTitle'] = "%s %s %s" % (
            be.bpModel.type.description,
            be.bpModel.id, be.bpModel.displayName())
        cbContext.currentBp = be
        changeLog = ChangeHistory.objects.filter(objectId=cbContext.bpId, type='BP').order_by('-updatedAt')
        cbContext.changeLog = changeLog
        # attachments = OrderFileAttachment.objects.filter(order__id=coContext.orderId).order_by('-createdAt')
        # coContext.attachments = attachments
        setContext(request, cbCtxName, cbContext)
        AddObjectIdToHistory(request, context, cbContext.bpId, 'BP')

    def edit(self, request, context):
        cbContext = getContext(request, cbCtxName)
        cbContext.fieldErrors = {}
        if not cbContext.currentBp:
            if cbContext.bpId:
                model = self.loadCommonBp(cbContext.bpId, request, context)
                be = getBusinessPartnerEntity(cbContext.bpType, model, request)
                cbContext.currentBp = be
        context['commonBpTitle'] = "%s %s %s" % (
            cbContext.currentBp.bpModel.type.description,
            cbContext.currentBp.bpModel.id, cbContext.currentBp.bpModel.displayName())
        uid = request.session['up']['userloginid']
        userLogin = UserLogin.objects.get(id=uid)
        # Check lock and add lock
        lock = GetEntityLock(cbContext.bpId, 'BP', userLogin.userbp.id)
        if lock:
            self.initializeMessageBar(request, context)
            lockedByName = BP.objects.get(id=lock.lockedBy).displayName()
            lockInfo = u'该记录正在被 %s 编辑' % lockedByName
            context['messagebar'].extend([{'type': 'error',
                                           'content': lockInfo}])
            context['nav']['pageStatus'] = 'detail'
            return
        AddEntityLock(cbContext.bpId, 'BP', userLogin.userbp.id)
        cbContext.mode = 'edit'
        # attachments = OrderFileAttachment.objects.filter(order__id=coContext.orderId).order_by('-createdAt')
        # coContext.attachments = attachments
        setContext(request, cbCtxName, cbContext)
        super(CommonBpAppView, self).edit(request, context)

    def new(self, request, context):
        # User clicked new button
        # Create a default BP model and wrap as Business Entity by its type
        # Save this entity in session
        super(CommonBpAppView, self).new(request, context)
        # Get BP Type from pageParams
        bpType = request.POST.get('pageParams', None)
        cbContext = getContext(request, cbCtxName)
        cbContext.bpType = bpType
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        # Create new BP
        model = BP()
        model.type = BPType.objects.get(key=bpType)
        model.bpcustomized = BPCustomized()
        # Wrap as Business Entity
        be = getBusinessPartnerEntity(bpType, model, request)
        cbContext.currentBp = be
        # Clear bp id in context
        cbContext.bpId = None
        # Save in session and set mode to new
        cbContext.mode = 'new'
        setContext(request, cbCtxName, cbContext)

    def save(self, request, context):
        super(CommonBpAppView, self).save(request, context)
        context['messagebar'] = []
        errors = []
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        cbContext = getContext(request, cbCtxName)
        cbContext.fieldErrors = {}
        try:
            be = cbContext.currentBp
            # Start transaction
            with transaction.atomic():
                be.setCurrentUser(userBp)
                be.pageStatus = cbContext.mode
                if be.pageStatus == 'new':
                    # If mode is new, means it's may not be saved, save it
                    be.bpModel.save()
                fieldsOfBP = BPFieldDef.objects.filter(Q(bpType=be.bpModel.type),
                                                       ~Q(attributeType='Addon'))
                configuredFields = BPStdViewLayoutConf.objects.filter(field__in=fieldsOfBP, visibility=True,
                                                                      viewType__key='Detail', valid=True).order_by(
                    'locRow',
                    'locCol')
                changeLog = []
                for cf in configuredFields:
                    confData = GetFieldConfigData(be, cf)

                    # Get field phrase
                    phraseId = cf.labelPhraseId
                    if not phraseId:
                        phraseId = cf.field.fieldKey
                    fieldname = getPhrase(request, 'bp', phraseId)
                    # Ignore id field, it's not changable
                    if cf.field.fieldKey == 'id':
                        continue
                    fieldValue = request.POST.get(cf.field.fieldKey, None)

                    if not confData['editable']:
                        continue
                    # Call get method
                    try:
                        oldKeyValue, oldDisplayValue = GetFieldValue(be, **confData)
                        SetFieldValue(be, fieldValue, **confData)
                        newKeyValue, newDisplayValue = GetFieldValue(be, **confData)
                    except Exception, e:
                        cbContext.fieldErrors[confData['fieldKey']] = "%s %s" % (fieldname, e.message)

                    if str(oldKeyValue) != str(newKeyValue) or str(oldDisplayValue) != str(newDisplayValue):
                        oh = ChangeHistory()
                        oh.objectId = be.bpModel.id
                        oh.type = 'BP'
                        oh.objectField = confData['fieldKey']
                        oh.newValue = newDisplayValue
                        oh.newKeyValue = newKeyValue
                        oh.oldValue = oldDisplayValue
                        oh.oldKeyValue = oldKeyValue
                        oh.updatedBy = userBp.id
                        oh.updatedAt = datetime.datetime.now()
                        changeLog.append(oh)
                be.save()
                if len(cbContext.fieldErrors) > 0:
                    raise Exception("Error")
                for changelog in changeLog:
                    changelog.save()
            cbContext.bpId = be.bpModel.id
        except Exception, e:
            for key, error in cbContext.fieldErrors.items():
                errors.extend([{'type': 'error', 'content': error}])
            errors.extend([{'type': 'error', 'content': e.message}])

        # Save errors/info in context
        context['messagebar'].extend(errors)
        errs = [x for x in errors if x['type'] == 'error']
        if len(errs) != 0:
            cbContext.mode = 'edit'
            setContext(request, cbCtxName, cbContext)
            super(CommonBpAppView, self).edit(request, context)
            navPath = request.session.get('navPath', None)
            if len(navPath) > 1:
                del navPath[-1:]
        else:
            context['messagebar'].extend([{'type': 'success',
                                           'content': getPhrase(request, 'g_default', 'bpSaved', u"数据已保存")}])
            cbContext.mode = 'detail'
            DeleteEntityLock(cbContext.bpId, 'BP', userBp.id)
            setContext(request, cbCtxName, cbContext)
            navPath = request.session.get('navPath', None)
            if len(navPath) > 2:
                del navPath[-2:]
            self.view(request, context)

    def cancel(self, request, context):
        cbContext = getContext(request, cbCtxName)
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        DeleteEntityLock(cbContext.bpId, 'BP', userBp.id)
        if cbContext.currentBp and cbContext.mode != 'new':
            cbContext.mode = 'detail'
            setContext(request, cbCtxName, cbContext)
            context['commonBpTitle'] = "%s %s %s" % (
                cbContext.currentBp.bpModel.type.description,
                cbContext.currentBp.bpModel.id, cbContext.currentBp.bpModel.displayName())
            super(CommonBpAppView, self).cancel(request, context)
        else:
            self.initialize(request, context)

    def back(self, request, context):
        super(CommonBpAppView, self).back(request, context)
        return self.page

    def upload(self, request, context):
        fuf = FileUploadForm(request.POST, request.FILES)
        if fuf.is_valid():
            cbContext = getContext(request, cbCtxName)
            upfile = fuf.cleaned_data['file']
            fa = BPFileAttachment()
            fa.bp = cbContext.currentBp.bpModel
            fa.file = upfile
            fa.description = upfile.name
            fa.actualfilename = upfile.name
            fa.name = upfile.name
            userBp = getCurrentUserBp(request)
            fa.createdBy = userBp
            fa.save()
        super(CommonBpAppView, self).upload(request, context)

    def deletefile(self, request, context):
        fileId = context['nav']['pageParams']
        ofa = BPFileAttachment.objects.get(id=fileId)
        ofa.deleteFlag = True
        ofa.save()
        super(CommonBpAppView, self).deletefile(request, context)

    def download(self, request, context):
        fileId = context['nav']['pageParams']
        fa = BPFileAttachment.objects.get(id=fileId)
        filename = fa.actualfilename  # fa.file._get_path().split('/')[-1]
        data = fa.file._get_file().read()
        clientSystem = request.META['HTTP_USER_AGENT']
        if clientSystem.find('Windows') > -1:
            filename = filename.encode('cp936')
        else:
            filename = filename.encode('utf-8')
        response = HttpResponse(data, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    def leave(self, request, context):
        cbContext = getContext(request, cbCtxName)
        if cbContext:
            uid = request.session['up']['userloginid']
            userBp = UserLogin.objects.get(id=uid).userbp
            DeleteEntityLock(cbContext.bpId, 'BP', userBp.id)

    def xlsoutput(self, request, context):
        cbContext = getContext(request, cbCtxName)
        return getCommonOrderXLS(request, cbContext.resultHeaders, cbContext.resultItems)

    def loadCommonBp(self, commonBpId, request, context):
        model = BP.objects.get(id=commonBpId)
        mb = context.get('messagebar', None)
        if not mb:
            mb = context['messagebar'] = []
        # For SA01, check status
        # if model.ordercustomized.stage == '00005':
        #     mb.append({'type': 'info',
        #                'content': "Follow up order not finished"}
        #               )

        return model


# Get business entity name based on order type
def getBusinessEntity(orderType, model, request=None):
    beObj = OrderBEDef.objects.filter(orderType__key=orderType)
    if beObj:
        beName = beObj[0].businessEntity
    else:
        # Default entity
        beName = 'OrderBE'
    be = eval("%s(%s)" % (beName, 'model'))
    if request:
        # Set userid into Business Entity
        # Todo - This is not good, but how could I customized field based on user without knowing who he is?
        userLoginId = request.session['up']['userloginid']
        be.userLoginId = userLoginId
    return be


# Get partner entity name based on bp type
def getBusinessPartnerEntity(bpType, model, request=None):
    beObj = BPBEDef.objects.filter(bpType__key=bpType)
    if beObj:
        beName = beObj[0].businessEntity
    else:
        # Default entity
        beName = 'BPBE'
    be = eval("%s(%s)" % (beName, 'model'))
    if request:
        # Set userid into Business Entity
        # Todo - This is not good, but how could I customized field based on user without knowing who he is?
        userLoginId = request.session['up']['userloginid']
        be.userLoginId = userLoginId
    return be


def getCurrentUser(request):
    """The function reads up.userloginid from session and return UserLogin object"""
    userprofile = request.session.get('up', None)
    if not userprofile:
        return None
    userLoginId = userprofile.get('userloginid', None)
    if not userLoginId:
        return None
    ul = UserLogin.objects.get(id=userLoginId)
    return ul


def getCurrentUserBp(request):
    """The function reads up.userloginid from session and return BP object"""
    userLogin = getCurrentUser(request)
    return userLogin.userbp


def getPhrase(request, appid, phraseid, default=None):
    """The function return the phrase text against language in session"""
    startTime = time.time()
    lan = request.session.get('lan', 'cn')
    # Todo - cache phrase in memory later
    global phrase_cache
    if not phrase_cache:
        phrase_cache = SitePhrase.objects.all()
    p = phrase_cache.filter(app__appId=appid, phraseId=phraseid, phraseLan__key=lan)
    endTime = time.time()
    diff = endTime - startTime
    if p and p[0]:
        if p[0].content:
            return p[0].content
        else:
            return p[0].bigContent
    else:
        if default:
            return default
        else:
            return "[%s %s %s]" % (appid, phraseid, lan)


def getCurrentCompany():
    """The function return current company BP object(relation ZZ)"""
    com = BP.objects.filter(type__exact='ZZ', valid=True)
    if com:
        return com[0]
    else:
        return None


def verifyUser(username, password):
    """
    Verify user from database table and return UserProfile object
    Error code
    e01 Wrong username or password
    e02 Too many failures, locked
    """
    error = ''
    encryptedPwd = hashlib.sha1(password).hexdigest()
    # Check unencrypted password
    userLogin = UserLogin.objects.filter(username__exact=username, password=password, passwordEncrypted=False)
    if userLogin:
        # User's password not encrypted
        userModel = userLogin[0]
        userModel.password = encryptedPwd
        if not userModel.passwordEncrypted:
            userModel.passwordEncrypted = True
        # Save encrypted password
        userModel.save()
    # Check encrypted password
    userLogin = UserLogin.objects.filter(username__exact=username, password=encryptedPwd, passwordEncrypted=True)
    user = {}
    if userLogin:
        userModel = userLogin[0]
        if userModel.status == None:
            # Save default status ACTIVE if it's not set
            userModel.status = UserLoginStatus.objects.get(key='ACTIVE')
            userModel.save()
        elif userModel.status.key == 'LOCK':
            error = 'e02'
            return (None, error)
        elif userModel.status.key == 'CLOSED':
            error = 'e03'
            return (None, error)
        # Successfully login, clear failure count and record time
        userModel.failureCount = 0
        userModel.lastLoginAt = datetime.datetime.today()
        userModel.save()
        user['username'] = userModel.user.nickName
        user['userloginid'] = userModel.id
        # Get user roles, profiles, parameter, authorization
        user['userAuth'] = {}
        user['userAuth']['roles'] = [ur.role.key for ur in UserRole.objects.filter(userlogin=userLogin, valid=True)]
        user['userAuth']['profiles'] = [up.profile.key for up in
                                        UserProfile.objects.filter(userlogin=userLogin, valid=True)]
        user['userAuth']['parameters'] = [{parameter.name: parameter.value} for parameter in
                                          UserParameter.objects.filter(userlogin=userLogin)]
        return (user, None)
    else:
        # Either username or password wrong
        error = 'e01'
        userLogin = UserLogin.objects.filter(username__exact=username)
        if userLogin:
            # Found user by username, check status and add failure count
            userModel = userLogin[0]
            if userModel.status.key == 'LOCK':
                error = 'e02'
                return (None, error)
            elif userModel.status.key == 'CLOSED':
                error = 'e03'
                return (None, error)
            userModel.failureCount += 1
            # Lock if failed over 5 times
            if userModel.failureCount >= 5:
                userModel.status = UserLoginStatus.objects.get(key='LOCK')
                error = 'e02'
            userModel.save()
        # No access
        return (None, error)


def checkIsUserLogin(request):
    userProfile = request.session.get('up', None)
    return bool(userProfile)


def checkUserRole(request):
    userProfile = request.session.get('up', None)
    if not userProfile:
        return False
    loginRole = userProfile.get('loginRole', None)
    if not loginRole or loginRole == '':
        return False
    return True


def THR(request, template, context):
    """Return HttpResponse object with template and context"""
    template = loader.get_template(template)
    ctx = RequestContext(request, context)
    return HttpResponse(template.render(ctx))


# Create/update order partner relationship
# relatedOrder is a new parameter, to reduce the impact for current logic, this field
# is optional, if it's provided, it will be saved to relatedOrder column
def OrderPFNew_or_update(order, pf, bp, relatedOrder=None):
    """Update order partner function, add if not exist"""
    orderPF = order.orderpf_set.filter(pf__key=pf)
    if orderPF:
        if bp:
            orderPF[0].bp = bp
        if relatedOrder:
            orderPF[0].relatedOrder = relatedOrder
        orderPF[0].save()
    else:
        p = PFType.objects.filter(orderType=order.type, key=pf)
        if p:
            orderPF = OrderPF()
            orderPF.order = order
            orderPF.pf = p[0]
            if bp:
                orderPF.bp = bp
            if relatedOrder:
                orderPF.relatedOrder = relatedOrder
            orderPF.save()
            order.orderpf_set.add(orderPF)


# Add order partner relationship
# relatedOrder is new field added, to reduce impacts, it's optional
def OrderPFAdd(order, pf, bp, relatedOrder=None):
    """Add partner function"""
    # Get PFType
    pfType = PFType.objects.filter(orderType=order.type, key=pf)
    if not pfType:
        log.info('no pf type %s' % pf)
        return
    pfType = pfType[0]
    min = pfType.minimum
    max = pfType.maximum
    orderPF = OrderPF.objects.filter(order=order, pf=pf)
    if max and orderPF.count() < max:
        orderPF = OrderPF()
        orderPF.order = order
        orderPF.pf = pfType
        if bp:
            orderPF.bp = bp
        if relatedOrder:
            orderPF.relatedOrder = relatedOrder
        orderPF.save()
    else:
        log.info('reached max')


# Get partner functions from order
# This method will only get bp partner function
def OrderPFGet(order, pf):
    orderPF = order.orderpf_set.filter(pf__key=pf)
    if orderPF:
        return [o.bp.id for o in orderPF]
    else:
        return None


# Get partner functions from order
# This method will only get order partner function
def OrderPFGetOrder(order, pf):
    orderPF = order.orderpf_set.filter(pf__key=pf)
    if orderPF:
        return [o.relatedOrder.id for o in orderPF]
    else:
        return None


# Get single partner function from order
# This method return single BP partner function
def OrderPFGetSingleBP(order, pf):
    orderPF = order.orderpf_set.filter(pf__key=pf)
    if orderPF:
        return orderPF[0].bp
    else:
        return None


# Get single partner function order object from order
# This method return single order partner function
def OrderPFGetSingleOrder(order, pf):
    orderPF = order.orderpf_set.filter(pf__key=pf)
    if orderPF:
        return orderPF[0].relatedOrder
    else:
        return None


# Remove partner function from order
# relatedOrder is newly added, to reduce impacts, it's optional
def OrderPFDelete(order, pf, bp, relatedOrder=None):
    """Delete pf relationship from order in partner function"""
    if bp and relatedOrder:
        orderPFs = OrderPF.objects.filter(order=order, pf__key=pf, bp=bp, relatedOrder=relatedOrder)
    else:
        if bp:
            orderPFs = OrderPF.objects.filter(order=order, pf__key=pf, bp=bp)
        else:
            orderPFs = OrderPF.objects.filter(order=order, pf__key=pf)
    for orderPF in orderPFs:
        orderPF.delete()


# Return ordercustomized model, if not exists, create one
def GetOrderCustNew_or_update(order):
    if hasattr(order, 'ordercustomized'):
        orderCust = order.ordercustomized
        return orderCust
    else:
        orderCust = OrderCustomized()
        orderCust.order = order
        orderCust.save()
        return orderCust


# Get the entity value based on configuration data
def GetEntityValue(entity, **confData):
    """
    This method will read a field configured in confData from django model object
    :param orderModel: Django Order Model
    :param confData: Fields configuration data, table OrderFieldDef
    :return: (key, value) pair
    """
    # default return pair
    key, value = None, ''
    # Get configration
    storeColumn = confData.get('storeColumn', None)
    fieldKey = confData.get('fieldKey', None)
    storeType = confData.get('storeType', None)
    storeKey = confData.get('storeKey', None)
    fieldType = confData.get('fieldType', None)
    fieldColumn = bool(storeColumn) and storeColumn or fieldKey
    if hasattr(entity, 'orderModel'):
        orderModel = entity.orderModel
        if storeType == 'PF':
            # The field is a partner function field
            # Value stored in OrderPF table with PFType object of key name = 'storeKey'
            # Order   PFType  BP
            p = orderModel.orderpf_set.filter(pf__key=confData['storeKey'])
            if p:
                # Todo - Right now only 1 bp returned
                if storeColumn == 'Order':
                    key = p[0].relatedOrder.id
                    value = p[0].relatedOrder.description
                else:
                    key = p[0].bp.id
                    value = p[0].bp.displayName()
                return (key, value)
        elif storeType == 'Customized':
            # The field is store in ordercustomized
            if hasattr(orderModel, 'ordercustomized'):
                if hasattr(orderModel.ordercustomized, fieldColumn):
                    # Directly call model's method to get value
                    value = eval('orderModel.ordercustomized.%s' % fieldColumn)
                else:
                    # Error that column not found
                    value = u'ordercustomized上未找到字段%s' % fieldColumn
            else:
                value = u'未创建实体ordercustomized'
        elif storeType == 'Activity':
            # The field is store in ordercustomized
            if hasattr(orderModel, 'activity'):
                if hasattr(orderModel.activity, fieldColumn):
                    # Directly call model's method to get value
                    value = eval('orderModel.activity.%s' % fieldColumn)
                else:
                    # Error that column not found
                    value = u'activity上未找到字段%s' % fieldColumn
            else:
                value = u'未创建实体ordercustomized'
        elif storeType == 'Text':
            if hasattr(orderModel, 'ordertext_set'):
                txt = orderModel.ordertext_set.filter(type=storeKey).order_by('-createdAt')
                if txt:
                    value = txt[0].content
        elif storeType == 'MultipleValue':
            if hasattr(orderModel, 'ordermultiplevaluefield_set'):
                key = value = [{"id": str(r.id), "charValue1": r.charValue1, "charValue2": r.charValue2} for r in
                               orderModel.ordermultiplevaluefield_set.filter(field__fieldKey=confData['fieldKey'])]
        else:
            # By default, try column on Order model
            if hasattr(orderModel, fieldColumn):
                value = eval('orderModel.%s' % fieldColumn)
            else:
                value = u'order上未找到%s' % fieldColumn
        if storeKey and fieldType == 'SE' or fieldType == 'MS':
            # If field is a selection field
            # Selection options defined in OrderExtSelectionFieldType
            # Retrieve the selection description instead of key
            # The value is actually the selection key
            key = value
            # Get description from OrderExtSelectionFieldType
            value = orderModel.type.orderextselectionfieldtype_set.filter(fieldKey=storeKey, key=value)
            if value:
                value = value[0].description
            else:
                value = ''
        if fieldType == 'IF' or fieldType == 'FI':
            if value or value._file:
                key = value
                value = key._get_path().split('/')[-1]
            else:
                key = ''
                value = ''
    elif hasattr(entity, 'bpModel'):
        bpModel = entity.bpModel
        if False:
            pass
        elif storeType == 'Customized':
            # The field is store in bpcustomized
            if hasattr(bpModel, 'bpcustomized'):
                if hasattr(bpModel.bpcustomized, fieldColumn):
                    # Directly call model's method to get value
                    value = eval('bpModel.bpcustomized.%s' % fieldColumn)
                else:
                    # Error that column not found
                    value = u'bpcustomized上未找到字段%s' % fieldColumn
            else:
                value = u'未创建实体bpcustomized'
        elif storeType == 'Text':
            if hasattr(bpModel, 'bptext_set'):
                txt = bpModel.bptext_set.filter(type=storeKey).order_by('-createdAt')
                if txt:
                    value = txt[0].content
        else:
            if hasattr(bpModel, fieldColumn):
                value = eval('bpModel.%s' % fieldColumn)
            else:
                value = u'bp上未找到%s' % fieldColumn
        if fieldType == 'IF' or fieldType == 'FI':
            if value or value._file:
                key = value
                value = key._get_path().split('/')[-1]
            else:
                key = ''
                value = ''
    else:
        pass
    return (key, value)


# Set the entity value based on configuration data
def SetEntityValue(entity, value, **confData):
    """
    This method set field value into Django Order model based on field configuration
    :param orderModel: Order model object
    :param confField: StdViewLayoutConf object
    :param value: value that need to be saved
    :return: won't return any value
    """
    storeColumn = confData.get('storeColumn', None)
    fieldKey = confData.get('fieldKey', None)
    storeType = confData.get('storeType', None)
    storeKey = confData.get('storeKey', None)
    required = confData.get('required', False)
    fieldColumn = bool(storeColumn) and storeColumn or fieldKey
    # Check value type
    if confData['valueType'] == 'Number':
        try:
            int(value)
            float(value)
        except Exception, e:
            raise Exception(u"非数字类型")
    elif confData['valueType'] == 'Boolean':
        try:
            bool(value)
        except Exception, e:
            raise Exception(u"非布尔类型")
    else:
        pass
    if hasattr(entity, 'orderModel'):
        orderModel = entity.orderModel
        if storeType == 'PF' and storeKey:
            if value:
                OrderPFNew_or_update(orderModel, storeKey, BP.objects.get(id=value))
            else:
                OrderPFDelete(orderModel, storeKey, None)
        elif storeType == 'Customized':
            if not hasattr(orderModel, 'ordercustomized'):
                # If no OrderCustomized record, create one
                orderModel.ordercustomized = OrderCustomized()
                orderModel.ordercustomized.save()
                orderModel.save()
            if hasattr(orderModel.ordercustomized, fieldColumn):
                if confData['fieldType'] == 'IF':
                    if value:
                        if int(value) > 0:
                            uploadFilesTemp = UploadFilesTemp.objects.get(id=value)
                            exec (
                                "orderModel.ordercustomized.%s.save(uploadFilesTemp.imageFile._get_path().split('/')[-1],uploadFilesTemp.imageFile)" % (
                                    fieldColumn,))
                            filepath = uploadFilesTemp.imageFile.path
                            uploadFilesTemp.delete();
                            os.remove(filepath)
                        else:
                            exec ("orderModel.ordercustomized.%s=None" % (fieldColumn,))
                elif confData['fieldType'] == 'FI':
                    if value:
                        if int(value) > 0:
                            uploadFilesTemp = UploadFilesTemp.objects.get(id=value)
                            exec (
                                "orderModel.ordercustomized.%s.save(uploadFilesTemp.normalFile._get_path().split('/')[-1],uploadFilesTemp.normalFile)" % (
                                    fieldColumn,))
                            filepath = uploadFilesTemp.normalFile.path
                            uploadFilesTemp.delete();
                            os.remove(filepath)
                        else:
                            exec ("orderModel.ordercustomized.%s=None" % (fieldColumn,))
                else:
                    if value is None:
                        exec ("orderModel.ordercustomized.%s=None" % fieldColumn)
                    else:
                        if confData['valueType'] in ['Number', 'Boolean']:
                            # Number type
                            exec ("orderModel.ordercustomized.%s=%s" % (fieldColumn, value))
                        else:
                            # String type
                            exec ("orderModel.ordercustomized.%s='%s'" % (fieldColumn, value))
                orderModel.ordercustomized.save()
            else:
                raise Exception(u"%s not found on ordercustomized" % fieldColumn)
        elif storeType == 'MultipleValue':
            # Value is a json object
            jsonValue = json.loads(value)
            # Remove records whose id not in current jsonValue
            ids = []
            newToCreate = []
            for value in jsonValue:
                if str(value['id']).startswith('new'):
                    newToCreate.append(value)
                else:
                    ids.append(value['id'])
            if ids:
                for order in orderModel.ordermultiplevaluefield_set.filter(~Q(id__in=ids),
                                                                           Q(field__fieldKey=confData['fieldKey'])):
                    order.delete()
            if not jsonValue:
                for order in orderModel.ordermultiplevaluefield_set.filter(Q(field__fieldKey=confData['fieldKey'])):
                    order.delete()
            # Add new record if any
            for value in newToCreate:
                omvf = OrderMultipleValueField()
                omvf.order = orderModel
                omvf.field = orderModel.type.orderfielddef_set.filter(fieldKey=confData['fieldKey'])[0]
                omvf.charValue1 = value.get('charValue1', None)
                omvf.charValue2 = value.get('charValue2', None)
                orderModel.ordermultiplevaluefield_set.add(omvf)
                orderModel.save()
        elif storeType == 'Activity':
            if not hasattr(orderModel, 'activity'):
                # If no OrderCustomized record, create one
                # orderModel.activity = Activity()
                activity = Activity()
                activity.order = orderModel
                activity.save()
                orderModel.activity = activity
                orderModel.save()
            orderModel.activity.order = orderModel
            orderModel.activity.save()
            if hasattr(orderModel.activity, fieldColumn):
                if value is None:
                    exec ("orderModel.activity.%s=None" % fieldColumn)
                else:
                    if confData['valueType'] in ['Number', 'Boolean']:
                        # Number type
                        exec ("orderModel.activity.%s=%s" % (fieldColumn, value))
                    else:
                        # String type
                        exec ("orderModel.activity.%s='%s'" % (fieldColumn, value))
                orderModel.activity.save()
            else:
                raise Exception(u"%s not found on ordercustomized" % fieldColumn)
        elif storeType == 'Text' and storeKey:
            if value:
                newText = OrderText()
                newText.order = orderModel
                newText.type = TextType.objects.get(pk=storeKey)
                newText.content = value
                newText.createdBy = orderModel.updatedBy
                newText.save()
        else:
            # Check field on Order model
            if hasattr(orderModel, fieldColumn):
                if value is None:
                    exec ("orderModel.%s=None" % fieldColumn)
                else:
                    if confData['valueType'] in ['Number', 'Boolean']:
                        exec ("orderModel.%s=%s" % (fieldColumn, value))
                    else:
                        exec ("orderModel.%s='%s'" % (fieldColumn, value))
                orderModel.save()
            else:
                raise Exception(u'order上未找到字段%s' % fieldColumn)
    elif hasattr(entity, 'bpModel'):
        bpModel = entity.bpModel
        if storeType == 'Customized':
            if not hasattr(bpModel, 'bpcustomized'):
                # If no BPCustomized record, create one
                bpModel.bpcustomized = BPCustomized()
                bpModel.bpcustomized.save()
                bpModel.save()
            else:
                if bpModel.bpcustomized.id is None:
                    bpModel.bpcustomized.bp = bpModel
                    bpModel.bpcustomized.save()
                    bpModel.save()
            if hasattr(bpModel.bpcustomized, fieldColumn):
                if confData['fieldType'] == 'IF':
                    if value:
                        if int(value) > 0:
                            uploadFilesTemp = UploadFilesTemp.objects.get(id=value)
                            exec (
                                "bpModel.bpcustomized.%s.save(uploadFilesTemp.imageFile._get_path().split('/')[-1],uploadFilesTemp.imageFile)" % (
                                    fieldColumn,))
                            filepath = uploadFilesTemp.imageFile.path
                            uploadFilesTemp.delete();
                            os.remove(filepath)
                        else:
                            exec ("bpModel.bpcustomized.%s=None" % (fieldColumn,))
                elif confData['fieldType'] == 'FI':
                    if value:
                        if int(value) > 0:
                            uploadFilesTemp = UploadFilesTemp.objects.get(id=value)
                            exec (
                                "bpModel.bpcustomized.%s.save(uploadFilesTemp.normalFile._get_path().split('/')[-1],uploadFilesTemp.normalFile)" % (
                                    fieldColumn,))
                            filepath = uploadFilesTemp.normalFile.path
                            uploadFilesTemp.delete();
                            os.remove(filepath)
                        else:
                            exec ("bpModel.bpcustomized.%s=None" % (fieldColumn,))
                else:
                    if value is None:
                        exec ("bpModel.bpcustomized.%s=None" % fieldColumn)
                    else:
                        if confData['valueType'] in ['Number', 'Boolean']:
                            # Number type
                            exec ("bpModel.ordercustomized.%s=%s" % (fieldColumn, value))
                        else:
                            # String type
                            exec ("bpModel.ordercustomized.%s='%s'" % (fieldColumn, value))
                bpModel.bpcustomized.save()
            else:
                raise Exception(u"%s not found on bpcustomized" % fieldColumn)
        elif storeType == 'Text' and storeKey:
            newText = BPText()
            newText.bp = bpModel
            newText.type = BPTextType.objects.get(pk=storeKey)
            newText.content = value
            newText.createdBy = bpModel.updatedBy
            newText.save()
        else:
            # Check field on BP model
            if hasattr(bpModel, fieldColumn):
                if value is None:
                    exec ("bpModel.%s=None" % fieldColumn)
                else:
                    if confData['valueType'] in ['Number', 'Boolean']:
                        exec ("bpModel.%s=%s" % (fieldColumn, value))
                    else:
                        exec ("bpModel.%s='%s'" % (fieldColumn, value))
                bpModel.save()
            else:
                raise Exception(u'bp上未找到字段%s' % fieldColumn)


def WrapSaleLeadOrder(order):
    """ Add customized fields to each order object and return the same """
    pfs = order.orderpf_set.all()
    for pf in pfs:
        if pf.pf.key == '00001':
            order.customer = pf.bp
        elif pf.pf.key == '00002':
            order.channel = pf.bp
        elif pf.pf.key == '00003':
            # log.info('add emp')
            order.empResp = pf.bp
            # else:
            # log.info('no pf')
    texts = order.ordertext_set.all()
    if texts:
        texts = texts.order_by('-createdAt')
        order.latestText = texts[0].content
    else:
        order.latestText = ''
    return order


def WrapSaleLeadOrders(orders):
    """This method will put partner function into fields of order
       It will also sort orders by stage sorting order
           Notice this will return a list object, instead of QuerySet, do use it just before set to context
"""
    st = time.time()
    stagesInOrder = OrderExtSelectionFieldType.objects.filter(fieldKey='00003').order_by('-sortOrder')
    sortedOrders = []
    result = []
    # Change the order into new result, change on parameter orders doesn't help
    # sortedOrders = [orders.get(id=o.id) for o in sorders]
    for stage in stagesInOrder:
        result = orders.filter(ordercustomized__stage=stage.key)
        sortedOrders += result
    # Loop the partner function set
    et = time.time()
    log.info('Resort orders by stage took %s' % (et - st))
    st = time.time()
    for order in sortedOrders:
        order = WrapSaleLeadOrder(order)
    et = time.time()
    log.info('Wrap orders took %s' % (et - st))
    return sortedOrders


def GetValueFromPOSTOrSession(request, key):
    """ Get value from request post, if not, get from session"""
    v = request.POST.get(key, None)
    if v:
        request.session[key] = v
    else:
        v = request.session.get(key, None)
    return v


def isCurrentUser(request, uid):
    up = request.session.get('up', None)
    if up:
        userid = up.get('userloginid', None)
        if userid and userid == uid:
            return True
    return False


def getXLS(request, models, heads):
    """
    heads like [{'col':'A','desc':'Column A'}]
    models like [{'A':'value A','B':'value B'}]
    """
    col_length = len(heads)
    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet('untitled')
    for i in range(col_length):
        sheet.write(0, i, heads[i]['desc'], style=xlwt.Style.default_style)
    i = 1
    for model in models:
        for k in range(col_length):
            log.info('%s %s %s' % (i, k, model[heads[k]['col']]))
            sheet.write(i, k, model[heads[k]['col']], style=xlwt.Style.default_style)
        i += 1

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=example.xls'
    book.save(response)
    return response


def getCommonOrderXLS(request, heads, results):
    """
    heads like [{'col':'A','desc':'Column A'}]
    models like [{'A':'value A','B':'value B'}]
    """
    col_length = len(heads)
    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet('untitled')
    for i in range(col_length):
        sheet.write(0, i, heads[i], style=xlwt.Style.default_style)
    i = 1
    for re in results:
        for k in range(col_length):
            log.info('%s %s %s' % (i, k, re[k]))
            sheet.write(i, k, re[k], style=xlwt.Style.default_style)
        i += 1

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=example.xls'
    book.save(response)
    return response


def getOrderStatics(orders):
    """
    return turple with SA01 order count, sum of travel amount and amount
        e.g. (10,500,700)
    """
    count = orders.count()
    sum = orders.aggregate(Sum('ordercustomized__travelAmount'), Count('id'))
    totalTravelAmount = sum.get('ordercustomized__travelAmount__sum', 0)
    sum = orders.aggregate(Sum('ordercustomized__amount'), Count('id'))
    totalAmount = sum.get('ordercustomized__amount__sum', 0)
    # Sum may become None if no records
    if totalTravelAmount is None:
        totalTravelAmount = 0
    if totalAmount is None:
        totalAmount = 0
    return (count, totalTravelAmount, totalAmount)


def parseFilter(filter, context):
    if type(filter) == str or type(filter) == unicode:
        v = filter
    else:
        v = filter.resolve(context)
        if v == '':
            v = filter
    return v


# Check whether user meet authorization requirement
def checkAuthObject(context, **p):
    name = p.get('name', None)
    value = p.get('value', None)
    value2 = p.get('value2', None)
    authPass = False
    up = context.get('up', None)
    if not up:
        return authPass
    if name == 'role' and value == up['loginRole']:
        authPass = True
    if name == 'profile' and value in up['userAuth']['profiles']:
        authPass = True
    if name == 'parameter' and {value: value2} in up['userAuth']['parameters']:
        authPass = True
    if name == 'auth':
        # Check all user profiles whether contains authorization object
        # C 1
        # R   1
        # U     1
        # D       1
        authValueInt = int(value2)
        userLogin = UserLogin.objects.get(id=up['userloginid'])
        ao = []
        # Check user single authorization objects
        au = [a.singleAuthObject for a in
              UserSingleAuthObject.objects.filter(userlogin=userLogin, singleAuthObject__authObject=value, valid=True)]
        if au:
            ao.append(au[0])
        # Check user profiles
        userProfiles = [p.profile for p in UserProfile.objects.filter(userlogin=userLogin, valid=True)]
        pau = [p.singleAuthObject for p in
               UserProfileAuthObject.objects.filter(profile__in=userProfiles, singleAuthObject__authObject=value,
                                                    valid=True)]
        if pau and pau[0]:
            ao.append(pau[0])
        if ao:
            au = ao[0]
            authValueInt = 0
            authValueInt |= bool(au.create) and 8 or 0
            authValueInt |= bool(au.read) and 4 or 0
            authValueInt |= bool(au.update) and 2 or 0
            authValueInt |= bool(au.delete) and 1 or 0
            if authValueInt & int(value2) == int(value2):
                authPass = True
    return authPass


def getUserAuthorization(context, authName):
    up = context.get('up', None)
    if up:
        userLogin = UserLogin.objects.get(id=up['userloginid'])
        ao = []
        # Check user single authorization objects
        au = [a.singleAuthObject for a in
              UserSingleAuthObject.objects.filter(userlogin=userLogin,
                                                  singleAuthObject__authObject=authName,
                                                  valid=True)]
        if au:
            ao.append(au[0])
        # Check user profiles
        userProfiles = [p.profile for p in UserProfile.objects.filter(userlogin=userLogin, valid=True)]
        pau = [p.singleAuthObject for p in
               UserProfileAuthObject.objects.filter(profile__in=userProfiles,
                                                    singleAuthObject__authObject=authName,
                                                    valid=True)]
        if pau and pau[0]:
            ao.append(pau[0])
        if ao:
            au = ao[0]
            return (au.create, au.read, au.update, au.delete)
    return (False, False, False, False)


def getEChartOptionTemplate():
    """ Return a template EChart options dictionary"""
    option = {
        'title': {
            'text': '',
            'subtext': '',
            'x': 'center'
        },
        'tooltip': {
            'trigger': 'item',
            # 'formatter': "{a} <br/>{b} : {c} ({d}%)"
            'formatter': "{b} : {c} ({d}%)"
        },
        'legend': {
            'orient': 'vertical',
            'x': 'left',
            'data': []
        },
        # 'toolbox': {
        #  'show' : 'true',
        #  'feature' : {
        #    'mark' : {'show': 'true'},
        #    'dataView' : {'show': 'true', 'readOnly': 'false'},
        #    'magicType' : {
        #    'show': 'true',
        #    'type': ['pie', 'funnel'],
        #    'option': {
        #      'funnel': {
        #        'x': '25%',
        #        'width': '50%',
        #        'funnelAlign': 'left',
        #        'max': '1548'
        #      }
        #    }
        #  },
        #  'restore' : {'show': 'true'},
        #  'saveAsImage' : {'show': 'true'}
        # }
        # },
        'calculable': 'true',
        'series': [{
            'name': '',
            'type': 'pie',
            'radius': '55%',
            'center': ['50%', '60%'],
            'data': []
        }
        ]
    }
    return option


def getHighChartOptionTemplate():
    option = {
        'chart': {
            'type': 'funnel',
            'marginRight': 100,
            'marginTop': 10
        },
        'title': {
            'title': '',
            'y': -50
        },
        'exporting': {
            'enabled': False
        },
        'plotOptions': {
            'series': {
                'dataLabels': {
                    'enabled': 'true',
                    'format': '<b>{point.name}</b> ({point.y:,.0f})',
                    'color': 'black',
                    'softConnector': 'true'
                },
                'neckWidth': '0%',
                'neckHeight': '0%'
            }
        },
        'legend': {
            'enabled': 'false'
        },
        'series': {}
    }
    return option


class BusinessEntity:
    def __init__(self, orderModel):
        self.orderModel = orderModel

    def setCurrentUser(self, userBp):
        self.currentUser = userBp

    def getCurrentUser(self):
        return self.currentUser

    def setPreviousOrderModel(self, orderModel):
        self.previousOrderModel = orderModel

    def getPreviousOrderModel(self):
        return self.previousOrderModel

    def save(self):
        if self.currentUser:
            self.orderModel.updatedBy = self.currentUser
        self.orderModel.save()


# Each Business Entity object bounded to Order Model(django model, table Order)
# The entity should be filled with correct Order model, that is, has a database record read
class OrderBE(BusinessEntity):
    """ OrderBE wrap a Order model
    Common fields are 'id','type','description','status','priority','createdAt','createdBy','updatedAt','updatedBy'
    Support methods:
    get_<fieldname>  return a turple (key/real value,description)
    set_<fieldname>
    get_<fieldname>_prop

    """

    def __init__(self, orderModel):
        BusinessEntity.__init__(self, orderModel)

    # Id
    def get_id(self):
        return (self.orderModel.id, self.orderModel.id)

    def set_id(self, id):
        pass

    def get_id_prop(self, property):
        if property == 'editable':
            return False

    # Type
    def get_type(self):
        return (self.orderModel.type.key, self.orderModel.type.description)

    def set_type(self, type):
        self.orderModel.type = OrderType.objects.get(key=type)

    def get_type_options(self):
        result = {}
        for s in OrderType.objects.all():
            result[s.key] = s.description
        return result

    # Description
    def get_description(self):
        return (None, self.orderModel.description)

    def set_description(self, desc):
        self.orderModel.description = desc

    # Status
    def get_status(self):
        if self.orderModel.status:  # hasattr(self.orderModel,'status'):
            return (self.orderModel.status.key, self.orderModel.status.description)
        else:
            return (None, '')

    def set_status(self, status):
        self.orderModel.status = StatusType.objects.get(orderType=self.orderModel.type, key=status)

    def get_status_options(self):
        """ Take effect if status field configured as SE """
        result = {}
        for s in StatusType.objects.filter(orderType=self.orderModel.type).order_by('sortOrder'):
            result[s.key] = s.description
        return result

    # Priority
    def get_priority(self):
        if self.orderModel.priority:  # hasattr(self.orderModel, 'priority'):
            return (self.orderModel.priority.key, self.orderModel.priority.description)
        else:
            return (None, '')

    def set_priority(self, priority):
        self.orderModel.priority = PriorityType.objects.get(orderType=self.orderModel.type, key=priority)

    def get_priority_options(self):
        """ Take effect if priority field configured as SE """
        result = {}
        for s in PriorityType.objects.filter(orderType=self.orderModel.type).order_by('-sortOrder'):
            result[s.key] = s.description
        return result

    # CreatedAt
    def get_createdAt(self):
        date = self.orderModel.createdAt
        date = timezone.localtime(date)
        if date:
            return (date, date.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            return (None, '')

    # def set_createdBy(self, bpId):
    #     self.orderModel.createdBy = bpId
    # CreatedBy
    def get_createdBy(self):
        return (self.orderModel.createdBy.id, self.orderModel.createdBy.displayName())

    def set_createdBy(self, bpId):
        self.orderModel.createdBy = bpId

    # UpdatedAt
    def get_updatedAt(self):
        date = self.orderModel.updatedAt
        date = timezone.localtime(date)
        if date:
            return (date, date.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            return (None, '')

    # UpdatedBy
    def get_updatedBy(self):
        return (self.orderModel.updatedBy.id, self.orderModel.updatedBy.displayName())

    def set_updatedBy(self, bpId):
        self.orderModel.updatedBy = bpId


class SaleOrderBE(OrderBE):
    """ SaleOrderBE wrap a Order model for sales
    """

    def __init__(self, orderModel):
        OrderBE.__init__(self, orderModel)
        self.pageStatus = ''
        # Private variable for field value
        # To save user enters while no actual related record available ( such as new creation)
        self.__customerId = None
        self.__channelId = None
        self.__empRespId = None
        # Only cache queryset of fields that unlikely to be changed
        self.oesft = OrderExtSelectionFieldType.objects.filter(orderType=orderModel.type)
        self.texts = orderModel.ordertext_set.all().order_by('-createdAt')
        if self.texts:
            self.latestText = self.texts[0].content
        else:
            self.latestText = ''

    def get_customer(self):
        bp = OrderPFGetSingleBP(self.orderModel, '00001')
        if bp:
            return (bp.id, bp.displayName())
        if self.__customerId != '':
            bp = BP.objects.filter(id=self.__customerId)
            if bp:
                return (self.__customerId, bp[0].displayName())
        return ('', '')

    def set_customer(self, customerId):
        self.__customerId = customerId
        if customerId is None or customerId == '':
            raise Exception(u"不能为空")
        customer = BP.objects.get(id=customerId)
        count = Order.objects.filter(deleteFlag=False, type=self.orderModel.type, orderpf__pf='00001',
                                     orderpf__bp=customer).count()
        if count != 0:
            raise Exception(u"已存在该客户的销售线索")
        OrderPFNew_or_update(self.orderModel, '00001', BP.objects.get(id=customerId))

    def get_customer_prop(self, property):
        if property == 'editable':
            if hasattr(self, 'pageStatus'):
                return self.pageStatus == 'new'

    def get_customer_options(self):
        result = {}
        for bpr in BPRelation.objects.filter(relation__exact='C1'):
            result[bpr.bpB.id] = bpr.bpB.name1
        return result

    def get_channel(self):
        bp = OrderPFGetSingleBP(self.orderModel, '00002')
        if bp:
            return (bp.id, bp.displayName())
        if self.__channelId != '':
            bp = BP.objects.filter(id=self.__channelId)
            if bp:
                return (self.__channelId, bp[0].name1)
        return ('', '')

    def set_channel(self, channelId):
        self.__channelId = channelId
        if channelId is None or channelId == '':
            raise Exception(u"不能为空")
        OrderPFNew_or_update(self.orderModel, '00002', BP.objects.get(id=channelId))

    def get_channel_options(self):
        result = {}
        for bpr in BPRelation.objects.filter(relation__exact='TM'):
            result[bpr.bpB.id] = bpr.bpB.name1
        return result

    def get_empResp(self):
        bp = OrderPFGetSingleBP(self.orderModel, '00003')
        if bp:
            return (bp.id, bp.displayName())
        if self.__empRespId != '':
            bp = BP.objects.filter(id=self.__empRespId)
            if bp:
                return (self.__empRespId, bp[0].displayName())
        return ('', '')

    def set_empResp(self, empRespId):
        self.__empRespId = empRespId
        if empRespId is None or empRespId == '':
            raise Exception(u"不能为空")
        OrderPFNew_or_update(self.orderModel, '00003', BP.objects.get(id=empRespId))

    def get_empResp_options(self):
        result = {}
        salesmen = GetEmployeeOfDepartment('SD')
        for salesman in salesmen:
            result[salesman.id] = salesman.displayName()
        return result

    def get_stage(self):
        stage = self.oesft.filter(fieldKey='00003', key=self.orderModel.ordercustomized.stage)
        if stage:
            return (stage[0].key, stage[0].description)
        else:
            return (None, '')

    def set_stage(self, stage):
        if stage is None or stage == '':
            raise Exception(u"不能为空")
        self.orderModel.ordercustomized.stage = self.oesft.filter(fieldKey='00003', key=stage)[0].key

    def get_stage_options(self):
        result = {}
        for ext in self.oesft.filter(fieldKey='00003'):
            result[ext.key] = ext.description
        return result

    def get_travelAmount(self):
        v = ''
        if hasattr(self.orderModel, 'ordercustomized'):
            v = self.orderModel.ordercustomized.travelAmount
            if not v:
                v = ''
        return (v, v)

    def set_travelAmount(self, travelAmount):
        travelAmount = travelAmount.strip(' ')
        if travelAmount == '':
            self.orderModel.ordercustomized.travelAmount = None
        else:
            self.orderModel.ordercustomized.travelAmount = travelAmount

    def get_goLiveDate(self):
        if hasattr(self.orderModel, 'ordercustomized'):
            date = self.orderModel.ordercustomized.goLiveDate
            if date:
                return (date.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d"))
            else:
                return (None, '')
        return (None, '')

    def set_goLiveDate(self, goLiveDate):
        if goLiveDate:
            dateObj = datetime.datetime.strptime(goLiveDate, '%Y-%m-%d')
            self.orderModel.ordercustomized.goLiveDate = dateObj
        else:
            self.orderModel.ordercustomized.goLiveDate = None

    def get_settleType(self):
        settleType = self.oesft.filter(fieldKey='00004', key=self.orderModel.ordercustomized.settleType)
        if settleType:
            return (settleType[0].key, settleType[0].description)
        else:
            return (None, '')

    def get_latestText(self):
        return (None, self.latestText)

    def get_text(self):
        logText = ''
        if self.pageStatus != 'edit':
            for l in self.texts.filter(type__key='T001').order_by('-createdAt'):
                # Build log
                t = '%s %s %s<br>----------<br>%s' % (
                    l.type.description, l.createdBy.displayName(),
                    timezone.localtime(l.createdAt).strftime('%Y-%m-%d %H:%M:%S'), l.content)

                logText = '%s%s<br><br>' % (logText, t)
        return (None, logText)

    def set_text(self, text):
        if text:
            self.newText = OrderText()
            self.newText.order = self.orderModel
            self.newText.type = TextType.objects.get(pk='T001')
            self.newText.content = text
            self.newText.createdBy = self.getCurrentUser()

    def get_acText(self):
        logText = ''
        if self.pageStatus != 'edit':
            for l in self.texts.filter(type__key='T003').order_by('-createdAt'):
                # Build log
                t = '%s %s %s<br>----------<br>%s' % (
                    l.type.description, l.createdBy.displayName(),
                    timezone.localtime(l.createdAt).strftime('%Y-%m-%d %H:%M:%S'), l.content)

                logText = '%s%s<br><br>' % (logText, t)
        return (None, logText)

    # Addon field, only get
    def get_district(self):
        if hasattr(self, 'customer'):
            if hasattr(self.customer, 'address1'):
                if hasattr(self.customer.address1, 'district'):
                    return (self.customer.address1.district.key, self.customer.address1.district.description)
        return (None, '')

    def get_district_options(self):
        result = {}
        for dis in DistrictType.objects.all():
            result[dis.key] = dis.description
        return result

    def save(self):
        if hasattr(self, 'newText'):
            self.newText.save()
        if hasattr(self.orderModel, 'ordercustomized'):
            self.orderModel.ordercustomized.order = self.orderModel
            self.orderModel.ordercustomized.save()
        OrderBE.save(self)


class ActivityBE(OrderBE):
    """
    The object may contains fields
    pageStatus
    userLoginId
    """

    def __init__(self, orderModel):
        OrderBE.__init__(self, orderModel)

    def get_startDateTime(self):
        if hasattr(self.orderModel, 'activity'):
            date = self.orderModel.activity.startDateTime
            if date:
                return (date.strftime("%Y-%m-%d %H:%M"), date.strftime("%Y-%m-%d %H:%M"))
            else:
                return (None, '')
        return (None, '')

    def set_startDateTime(self, startDateTime):
        if startDateTime:
            dateObj = datetime.datetime.strptime(startDateTime, '%Y-%m-%d %H:%M')
            self.orderModel.activity.startDateTime = dateObj
        else:
            self.orderModel.activity.startDateTime = None

    def get_endDateTime(self):
        if hasattr(self.orderModel, 'activity'):
            date = self.orderModel.activity.endDateTime
            if date:
                return (date.strftime("%Y-%m-%d %H:%M"), date.strftime("%Y-%m-%d %H:%M"))
            else:
                return (None, '')
        return (None, '')

    def set_endDateTime(self, endDateTime):
        if endDateTime:
            dateObj = datetime.datetime.strptime(endDateTime, '%Y-%m-%d %H:%M')
            self.orderModel.activity.endDateTime = dateObj
        else:
            self.orderModel.activity.endDateTime = None

    def get_customer_options(self):
        # For Activity, get only my customer
        # print self.userLoginId
        result = []
        userBp = UserLogin.objects.get(id=self.userLoginId).userbp
        orders = Order.objects.filter(deleteFlag=False, orderpf__pf__key='00003', orderpf__bp=userBp, type='SA01')
        opf = OrderPF.objects.filter(order__in=orders, pf__key='00001')
        for pf in opf:
            # o = order.orderpf_set.filter(pf__key='00001')
            result.append((pf.bp.id, pf.bp.displayName()))
        # for bpr in BPRelation.objects.filter(relation__exact='C1'):
        #     result[bpr.bpB.id] = bpr.bpB.name1
        # result.insert(0,('',''))
        return result


class CheckBE(OrderBE):
    def __init__(self, orderModel):
        OrderBE.__init__(self, orderModel)
        self.pageStatus = ''
        self.__orderId = None
        self.__empRespId = None
        self.texts = orderModel.ordertext_set.all().order_by('-createdAt')
        if self.texts:
            self.latestText = self.texts[0].content
        else:
            self.latestText = ''

    def get_checkOrder(self):
        order = OrderPFGetSingleOrder(self.orderModel, '00010')
        if order:
            return (order.id, order.description)
        elif self.__orderId != '':
            order = Order.objects.filter(id=self.__orderId)
            if order:
                return (self.__orderId, order[0].description)
        if hasattr(self, 'previousOrderModel') and self.previousOrderModel:
            return (self.previousOrderModel.id, self.previousOrderModel.description)
        return ('', '')

    def set_checkOrder(self, orderId):
        self.__orderId = orderId
        order = Order.objects.get(id=orderId)
        if order is None or orderId == '':
            OrderPFDelete(self.orderModel, '00010', None, order)
        else:
            OrderPFNew_or_update(self.orderModel, '00010', None, order)

    def get_checkOrder_options(self):
        result = {}
        for order in Order.objects.filter(type='SA01'):
            result[order.id] = order.description
        return result

    def get_checkOrder_prop(self, property):
        if property == 'fieldType':
            if self.pageStatus == 'edit' or self.pageStatus == 'new':
                return 'SE'
            else:
                return 'LK'
        elif property == 'fieldTypeLKHtml':
            orderId, _ = self.get_checkOrder()
            if orderId:
                order = Order.objects.get(id=orderId)
                return """<a href="javascript:toNav('commonOrder','view','%(orderId)s')">%(desc)s</a>""" % {
                    'orderId': order.id,
                    'desc': order.description
                }
            else:
                return ""
        elif property == 'editable':
            # Only salesman can edit
            rel = self.getCurrentUser().asBPB.filter(bpA__asBPB__bpA__asBPB__relation='SD')
            if rel:
                if property == 'editable':
                    if hasattr(self, 'pageStatus'):
                        return self.pageStatus == 'new'
            return False

    def get_description(self):
        if self.orderModel.description:
            return (None, self.orderModel.description)
        else:
            if hasattr(self, 'previousOrderModel') and self.previousOrderModel:
                pModelDesc = self.previousOrderModel.description
            else:
                pModelDesc = ''
            desc = "%s %s" % (self.orderModel.type.description, pModelDesc)
            return (None, desc)

    def set_description(self, desc):
        self.orderModel.description = desc

    def get_description_prop(self, property):
        if property == 'editable':
            # Only salesman can edit
            rel = self.getCurrentUser().asBPB.filter(bpA__asBPB__bpA__asBPB__relation='SD')
            if rel:
                return True
            else:
                return False

    def get_empResp(self):
        bp = OrderPFGetSingleBP(self.orderModel, '00003')
        if bp:
            return (bp.id, bp.displayName())
        if self.__empRespId != '':
            bp = BP.objects.filter(id=self.__empRespId)
            if bp:
                return (self.__empRespId, bp[0].displayName())
        return ('', '')

    def set_empResp(self, empRespId):
        self.__empRespId = empRespId
        if empRespId is None or empRespId == '':
            raise Exception(u"不能为空")
        OrderPFNew_or_update(self.orderModel, '00003', BP.objects.get(id=empRespId))

    def get_empResp_options(self):
        result = {}
        salesmen = GetEmployeeOfDepartment('OP')
        for salesman in salesmen:
            result[salesman.id] = salesman.displayName()
        return result

    def get_empResp_prop(self, property):
        if property == 'editable':
            # Only operation can edit
            rel = self.getCurrentUser().asBPB.filter(bpA__asBPB__bpA__asBPB__relation='OP')
            if rel:
                return True
            else:
                return False

    def get_checkResult_prop(self, property):
        if property == 'editable':
            # Only operation can edit
            rel = self.getCurrentUser().asBPB.filter(bpA__asBPB__bpA__asBPB__relation='OP')
            if rel:
                return True
            else:
                return False

    def get_status_prop(self, property):
        if property == 'editable':
            # Only operation can edit
            rel = self.getCurrentUser().asBPB.filter(bpA__asBPB__bpA__asBPB__relation='OP')
            if rel:
                return True
            else:
                return False

    def get_text(self):
        logText = ''
        if self.pageStatus != 'edit':
            for l in self.texts.order_by('-createdAt'):
                # Build log
                t = '%s %s %s<br>----------<br>%s' % (
                    l.type.description, l.createdBy.displayName(),
                    timezone.localtime(l.createdAt).strftime('%Y-%m-%d %H:%M:%S'), l.content)

                logText = '%s%s<br><br>' % (logText, t)
        return (None, logText)

    def save(self):
        OrderBE.save(self)
        orderId, _ = self.get_checkOrder()
        # Save order relationship
        orderA = Order.objects.get(id=orderId)
        # Get follow up definition
        followUpDefs = OrderFollowUpDef.objects.filter(orderTypeA=orderA.type, orderTypeB=self.orderModel.type)
        if followUpDefs:
            followUpDef = followUpDefs[0]
            # Check whether same relation exists, if not, save one
            OrderRel = OrderRelation.objects.filter(orderA=Order.objects.get(id=orderId), orderB=self.orderModel,
                                                    relation=followUpDef.relation)
            if not OrderRel:
                orderRel = OrderRelation()
                orderRel.orderA = Order.objects.get(id=orderId)
                orderRel.orderB = self.orderModel
                orderRel.relation = OrderRelType.objects.get(pk='FL')
                orderRel.save()


class OperationBE(OrderBE):
    def __init__(self, orderModel):
        OrderBE.__init__(self, orderModel)
        self.pageStatus = ''
        # Private variable for field value
        # To save user enters while no actual related record available ( such as new creation)
        self.__customerId = None
        self.__channelId = None
        self.__empRespId = None
        # Only cache queryset of fields that unlikely to be changed
        self.oesft = OrderExtSelectionFieldType.objects.filter(orderType=orderModel.type)
        self.texts = orderModel.ordertext_set.all().order_by('-createdAt')
        if self.texts:
            self.latestText = self.texts[0].content
        else:
            self.latestText = ''

    def get_customer_options(self):
        result = {}
        for bpr in BPRelation.objects.filter(relation__exact='C1'):
            result[bpr.bpB.id] = bpr.bpB.name1
        return result

    def get_customer(self):
        bp = OrderPFGetSingleBP(self.orderModel, '00001')
        if bp:
            return (bp.id, bp.displayName())
        if self.__customerId != '':
            bp = BP.objects.filter(id=self.__customerId)
            if bp:
                return (self.__customerId, bp[0].displayName())
        return ('', '')

    def set_customer(self, customerId):
        self.__customerId = customerId
        customer = BP.objects.get(id=customerId)
        if customerId is None or customerId == '':
            OrderPFDelete(self.orderModel, '00001', None)
        else:
            OrderPFNew_or_update(self.orderModel, '00001', customer)

    def get_empResp(self):
        bp = OrderPFGetSingleBP(self.orderModel, '00003')
        if bp:
            return (bp.id, bp.displayName())
        if self.__empRespId != '':
            bp = BP.objects.filter(id=self.__empRespId)
            if bp:
                return (self.__empRespId, bp[0].displayName())
        return ('', '')

    def set_empResp(self, empRespId):
        self.__empRespId = empRespId
        if empRespId is None or empRespId == '':
            raise Exception(u"不能为空")
        OrderPFNew_or_update(self.orderModel, '00003', BP.objects.get(id=empRespId))

    def get_empResp_options(self):
        result = {}
        for bpr in BPRelation.objects.filter(relation__exact='SF'):
            result[bpr.bpB.id] = bpr.bpB.displayName()
        return result

    def get_latestText(self):
        return (None, self.latestText)

    def get_text(self):
        logText = ''
        if self.pageStatus != 'edit':
            for l in self.texts.order_by('-createdAt'):
                # Build log
                t = '%s %s %s<br>----------<br>%s' % (
                    l.type.description, l.createdBy.displayName(),
                    timezone.localtime(l.createdAt).strftime('%Y-%m-%d %H:%M:%S'), l.content)

                logText = '%s%s<br><br>' % (logText, t)
        return (None, logText)

    def set_text(self, text):
        if text:
            self.newText = OrderText()
            self.newText.order = self.orderModel
            self.newText.type = TextType.objects.get(pk='T100')
            self.newText.content = text
            self.newText.createdBy = self.getCurrentUser()

    def save(self):
        if hasattr(self, 'newText'):
            self.newText.save()


class TestBE(OrderBE):
    def __init__(self, orderModel):
        OrderBE.__init__(self, orderModel)

    def get_customer_options(self):
        result = {}
        for bpr in BPRelation.objects.filter(relation__exact='C1'):
            result[bpr.bpB.id] = bpr.bpB.name1
        return result

    def get_customer2_options(self):
        result = {}
        for bpr in BPRelation.objects.filter(relation__exact='C1'):
            result[bpr.bpB.id] = bpr.bpB.name1
        return result

    def get_customer2_prop(self, property):
        if property == 'editable':
            if hasattr(self, 'pageStatus'):
                return self.pageStatus == 'new'


class BusinessPartnerEntity:
    def __init__(self, bpModel):
        self.bpModel = bpModel

    def setCurrentUser(self, userBp):
        self.currentUser = userBp

    def getCurrentUser(self):
        return self.currentUser

    def save(self):
        if self.currentUser:
            self.bpModel.updatedBy = self.currentUser
        self.bpModel.save()


class BPBE(BusinessPartnerEntity):
    def __init__(self, bpModel):
        BusinessPartnerEntity.__init__(self, bpModel)
        if bpModel.address1:
            self.__address = bpModel.address1
        else:
            self.__address = Address()
            self.__address.type = AddressType.objects.get(pk='ST')
        if hasattr(bpModel, 'bpcustomized'):
            self.__bpcustomized = bpModel.bpcustomized
        else:
            self.__bpcustomized = BPCustomized()
            self.__bpcustomized.bp = bpModel

    # Id
    def get_id(self):
        return (self.bpModel.id, self.bpModel.id)

    def set_id(self, id):
        pass

    def get_id_prop(self, property):
        if property == 'editable':
            return False

    # Type
    def get_type(self):
        return (self.bpModel.type.key, self.bpModel.type.description)

    def set_type(self, type):
        self.bpModel.type = BPType.objects.get(key=type)

    def get_type_options(self):
        result = {}
        for s in BPType.objects.all():
            result[s.key] = s.description
        return result

    # Partner No
    def get_partnerNo(self):
        return (self.bpModel.partnerNo, self.bpModel.partnerNo)

    def set_partnerNo(self, partnerNo):
        self.bpModel.partnerNo = partnerNo

    # Firstname
    def get_firstName(self):
        return (self.bpModel.firstName, self.bpModel.firstName)

    def set_firstName(self, firstName):
        self.bpModel.firstName = firstName

    # Middlename
    def get_middleName(self):
        return (self.bpModel.middleName, self.bpModel.middleName)

    def set_middleName(self, middleName):
        self.bpModel.middleName = middleName

    # Lastname
    def get_lastName(self):
        return (self.bpModel.lastName, self.bpModel.lastName)

    def set_lastName(self, lastName):
        self.bpModel.lastName = lastName

    # Name1
    def get_name1(self):
        return (self.bpModel.name1, self.bpModel.name1)

    def set_name1(self, name1):
        self.bpModel.name1 = name1

    # Name2
    def get_name2(self):
        return (self.bpModel.name2, self.bpModel.name2)

    def set_name2(self, name2):
        self.bpModel.name2 = name2

    # Address
    def get_address(self):
        return (self.__address.address1, self.__address.address1)

    def set_address(self, address):
        self.__address.address1 = address

    # District
    def get_district(self):
        if self.__address.district:
            return (self.__address.district.key, self.__address.district.description)
        else:
            return ('', '')

    def set_district(self, district):
        self.__address.district = DistrictType.objects.get(pk=district)

    def get_district_options(self):
        result = {}
        for s in DistrictType.objects.all():
            result[s.key] = s.description
        return result

    # Phone
    def get_phone(self):
        return (self.__address.phone1, self.__address.phone1)

    def set_phone(self, phone):
        self.__address.phone1 = phone

    # Contact
    def get_contact(self):
        return (self.__address.contact1, self.__address.contact1)

    def set_contact(self, contact):
        self.__address.contact1 = contact

    # Legal person
    def get_legalPerson(self):
        return (self.__bpcustomized.legalPerson, self.__bpcustomized.legalPerson)

    def set_legalPerson(self, legalPerson):
        self.__bpcustomized.legalPerson = legalPerson

    # Actual person
    def get_actualPerson(self):
        return (self.__bpcustomized.actualPerson, self.__bpcustomized.actualPerson)

    def set_actualPerson(self, actualPerson):
        self.__bpcustomized.actualPerson = actualPerson

    # Corp Structure
    def get_corpStructure(self):
        return (self.__bpcustomized.corpStructure, self.__bpcustomized.corpStructure)

    def set_corpStructure(self, corpStructure):
        self.__bpcustomized.corpStructure = corpStructure

    # # Corporation liscense image file
    # def get_corpLiscense(self):
    #     if self.__bpcustomized.corpLiscense:
    #         return (self.__bpcustomized.corpLiscense, self.__bpcustomized.corpLiscense.name)
    #     else:
    #         return ('','')
    #
    # def get_corpLiscense(self, corpLiscense):
    #     pass

    def save(self):
        self.bpModel.save()
        self.__bpcustomized.bp = self.bpModel
        self.__bpcustomized.save()
        self.__address.save()
        self.bpModel.address1 = self.__address
        BusinessPartnerEntity.save(self)


# Search Entity represent search criterias on search screen
class SearchEntity:
    def __init__(self):
        pass


# class OrderSearchEntity(SearchEntity):
#     def __init__(self):
#         SearchEntity.__init__(self)
#         self.id=''
#         self.



def buildSelectionOption(fieldname, options, currentValue, onchange):
    onchangeHtml = ''
    if onchange:
        onchangeHtml = ''.join(['onchange="', onchange, '"'])
    htmlOptions = ''.join(['<option value="%s" %s>%s</option>' % (
        kv['k'], bool(str(currentValue) == str(kv['k'])) and """selected = "selected" """ or "", kv['v']) for kv in
                           options])

    html = """<select class="" id="%s" name="%s" data-rel="" %s>
        %s
        </select >
            """ % (fieldname, fieldname, onchangeHtml, htmlOptions)
    return html


def buildSelectionOption2(fieldname, options, currentValue, onchange):
    onchangeHtml = ''
    if onchange:
        onchangeHtml = ''.join(['onchange="', onchange, '"'])
    htmlOptions = ''.join(['<option value="%s" %s>%s</option>' % (
        k, bool(str(currentValue) == str(k)) and """selected = "selected" """ or "", options[k]['v']) for k in
                           options.keys()])

    html = """<select class="" id="%s" name="%s" data-rel="" %s>
        %s
        </select >
            """ % (fieldname, fieldname, onchangeHtml, htmlOptions)
    return html


def buildDateInputBox(fieldname, placeholder, currentValue):
    html = """<input type="text" class="" style="height:21px" name="%s" id="%s_dp" placeholder="%s" value="%s">
                            <script>
     $(function() {
        $("#%s_dp").datepicker({ dateFormat: 'yy-mm-dd' });
      });
    </script>""" % (fieldname, fieldname, placeholder, currentValue, fieldname)
    return html


def buildDateTimeInputBox(fieldname, placeholder, currentValue):
    html = """<input type="text" class="" style="height:21px" name="%s" id="%s_dtp" placeholder="%s" value="%s">
                            <script>
     $(function() {
        $("#%s_dtp").datetimepicker({ dateFormat: 'yy-mm-dd hh:ii',startView:1});
      });
    </script>""" % (fieldname, fieldname, placeholder, currentValue, fieldname)
    return html


def GetFieldOptByType(fieldType, valueType, context):
    opts = {}
    possibleOpts = []
    if not valueType or valueType == 'String' or valueType == '':
        if fieldType == 'IN':
            possibleOpts = ['eq', 'ne', 'cs', 'nc']
        else:
            possibleOpts = ['eq', 'ne']
    elif valueType == 'Number' or valueType == 'Date':
        possibleOpts = ['eq', 'ne', 'gt', 'ge', 'lt', 'le', 'bt']
    elif valueType == 'Boolean':
        possibleOpts = ['eq', 'ne']
    else:
        possibleOpts = ['eq', 'ne']
    for o in possibleOpts:
        opts[o] = {'k': o, 'v': getPhrase(context['request'], 'g_default', o)}
    return opts


def buildInputBox(fieldname, placeholder, currentValue):
    html = """
<input type="text" class="" style="height:21px" name="%s" placeholder="%s" value="%s">
""" % (fieldname, placeholder, currentValue)
    return html


def modifySearchBeanFromFormData(request, searchBean):
    for i in range(len(searchBean.getList())):
        fn = 'fn%d' % i
        fo = 'fo%d' % i
        fl = 'fl%d' % i
        fh = 'fh%d' % i
        field = request.POST.get(fn, None)
        selectOption = searchBean.getSelectOptionAtIndex(i)
        selectOption.field = field
        if field != selectOption.field:
            selectOption.opt = 'eq'
            selectOption.low = ''
            selectOption.high = ''
        else:
            selectOption.opt = request.POST.get(fo, '')
            selectOption.low = request.POST.get(fl, '')
            selectOption.high = request.POST.get(fh, '')
        searchBean.setSelectOptionAtIndex(i, selectOption)


def getCommonOrderSearchFields(request, co):
    searchForm = []
    newSearchFields = []
    for i in range(0, len(co['sf'])):
        searchCriteria = {}
        fn = 'fn%d' % i
        fo = 'fo%d' % i
        fl = 'fl%d' % i
        fh = 'fh%d' % i
        field = request.POST.get(fn, None)
        if field != co['sf'][i]:
            searchCriteria['opt'] = 'eq'
            searchCriteria['low'] = ''
            searchCriteria['high'] = ''
        else:
            fieldOpt = request.POST.get(fo, '')
            searchCriteria['opt'] = fieldOpt
            fieldLow = request.POST.get(fl, '')
            searchCriteria['low'] = fieldLow
            fieldHigh = request.POST.get(fh, '')
            searchCriteria['high'] = fieldHigh
        searchCriteria['property'] = field
        searchForm.append(searchCriteria)
        newSearchFields.append(field)
    return (newSearchFields, searchForm)


def buildQobject(q, fieldname, opt, low, high, ao):
    if not low and not high:
        return
    conKey = fieldname
    # Special filter for status
    if fieldname == 'status':
        conKey = ''.join([fieldname, '__key'])
    # Special filter for priority
    if fieldname == 'priority':
        conKey = ''.join([fieldname, '__key'])
    # Operator mapping
    if opt == 'cs':
        conKey = ''.join([fieldname, '__icontains'])
        q.add(Q(**{conKey: low}), ao)
    elif opt == 'nc':
        conKey = ''.join([fieldname, '__icontains'])
        q.add(~Q(**{conKey: low}), ao)
    elif opt == 'eq':
        q.add(Q(**{conKey: low}), ao)
    elif opt == 'ne':
        q.add(~Q(**{conKey: low}), ao)
    elif opt == 'lt':
        conKey = ''.join([fieldname, '__lt'])
        q.add(Q(**{conKey: low}), ao)
    elif opt == 'le':
        conKey = ''.join([fieldname, '__lte'])
        q.add(Q(**{conKey: low}), ao)
    elif opt == 'gt':
        conKey = ''.join([fieldname, '__gt'])
        q.add(Q(**{conKey: low}), ao)
    elif opt == 'ge':
        conKey = ''.join([fieldname, '__gte'])
        q.add(Q(**{conKey: low}), ao)
    elif opt == 'bt':
        conKey = ''.join([fieldname, '__gte'])
        rq = Q()
        q1 = Q(**{conKey: low})
        conKey = ''.join([fieldname, '__lte'])
        q2 = Q(**{conKey: high})
        rq.add(q1, Q.AND)
        rq.add(q2, Q.AND)
        q.add(rq, ao)


def GetFieldConfigData(businessEntity, configuredField):
    """
    This method will populate field configration from database into dictionary.
    These value could be overwriten by Business Entity get_xxx_prop method
    :param businessEntity: Business Entity
    :param configuredField: Field configuration object
    :return: a dictionary
    """
    conf = {}
    conf['fieldKey'] = configuredField.field.fieldKey
    conf['fieldType'] = configuredField.field.fieldType.key
    conf['attributeType'] = configuredField.field.attributeType
    conf['valueType'] = configuredField.field.valueType
    conf['storeType'] = configuredField.field.storeType
    conf['storeColumn'] = configuredField.field.storeColumn
    conf['storeKey'] = configuredField.field.storeKey
    conf['locRow'] = configuredField.locRow
    conf['locCol'] = configuredField.locCol
    conf['locWidth'] = configuredField.locWidth
    conf['locHeight'] = configuredField.locHeight
    conf['labelPhraseId'] = configuredField.labelPhraseId
    conf['appId'] = configuredField.appId
    conf['editable'] = configuredField.editable
    conf['required'] = configuredField.required
    conf['multipleValue1PhraseId'] = configuredField.multipleValue1PhraseId
    conf['multipleValue1Required'] = configuredField.multipleValue1Required
    conf['multipleValue2PhraseId'] = configuredField.multipleValue2PhraseId
    conf['multipleValue2Required'] = configuredField.multipleValue2Required
    # Check and call get_<fieldname>_props
    # If no such method, use definition in database table
    callName = 'get_%s_prop' % conf['fieldKey']
    if hasattr(businessEntity, callName):
        parameters = ['fieldType', 'attributeType', 'valueType', 'storeType', 'storeColumn', 'storeKey', 'locRow',
                      'locCol', 'locWidth', 'locHeight', 'labelPhraseId', 'editable']
        for i in range(len(parameters)):
            callNameP = ''.join([callName, "('", parameters[i], "')"])
            result = eval("businessEntity.%s" % callNameP)
            if result is not None:
                conf[parameters[i]] = result
                if parameters[i] == 'fieldType' and result == 'LK':
                    callNameP = ''.join([callName, "('fieldTypeLKHtml')"])
                    result = eval("businessEntity.%s" % callNameP)
                    conf['fieldTypeLKHtml'] = result
    return conf


def GetFieldValueByFieldKey(businessEntity, fieldKey):
    fieldsOfOrder = OrderFieldDef.objects.filter(Q(orderType=businessEntity.orderModel.type), Q(fieldKey=fieldKey))
    configuredFields = StdViewLayoutConf.objects.filter(field__in=fieldsOfOrder, visibility=True,
                                                        viewType__key='Detail', valid=True).order_by('locRow', 'locCol')
    if configuredFields:
        configuredField = configuredFields[0]
        conf = GetFieldConfigData(businessEntity, configuredField)
        return GetFieldValue(businessEntity, **conf)
    elif fieldsOfOrder:
        field = fieldsOfOrder[0]
        conf = {}
        conf['fieldKey'] = field.fieldKey
        conf['fieldType'] = field.fieldType.key
        conf['attributeType'] = field.attributeType
        conf['valueType'] = field.valueType
        conf['storeType'] = field.storeType
        conf['storeColumn'] = field.storeColumn
        conf['storeKey'] = field.storeKey
        return GetFieldValue(businessEntity, **conf)
    else:
        return (None, '')


def GetFieldValue(businessEntity, **configuredData):
    """
    This method will read a field from Business Entity or Django model object
    :param businessEntity: Business Entity object, e.g Order, SaleOrder
    :param configuredData: Fields configuration data, table OrderFieldDef
    :return: (key, value) pair for field
    """
    # Create method name
    callName = 'get_%s' % configuredData['fieldKey']
    fieldValue, displayValue = '', ''
    if hasattr(businessEntity, callName):
        fieldValue, displayValue = eval('businessEntity.%s()' % callName)
    else:
        fieldValue, displayValue = GetEntityValue(businessEntity, **configuredData)
    if not fieldValue:
        fieldValue = displayValue
    return fieldValue, displayValue


def SetFieldValue(businessEntity, fieldValue, **configuredData):
    """
    This method set value to a field, it will try set_xxx on Business Entity or call SetOrderValue method
    :param businessEntity: Business Entity object
    :param fieldValue: value to set
    :param configuredData: field configurations
    :return: None
    """
    # If required, check whether field value is blank
    required = configuredData.get('required', False)
    if required and (fieldValue is None or fieldValue.strip() == ''):
        raise Exception(u"不可为空")
    # Call set method
    callName = 'set_%s' % configuredData['fieldKey']
    if hasattr(businessEntity, callName):
        # print "call be.%s(fieldValue)" % callName
        exec ("businessEntity.%s(fieldValue)" % callName)
    else:
        # No set method provided
        # Save by framework according to the configuration
        SetEntityValue(businessEntity, fieldValue, **configuredData)


def GetFieldValueAndOptions(businessEntity, **configuredData):
    """
    This method will get field key value, display value and options
    :param businessEntity: Business Entity object, e.g Order, SaleOrder
    :param configuredData: Fields configuration data, table OrderFieldDef
    :return: (fieldValue, displayValue, fieldOptions) tuple
    """
    fieldType = configuredData.get('fieldType', None)
    fieldKey = configuredData.get('fieldKey', None)
    storeType = configuredData.get('storeType', None)
    storeKey = configuredData.get('storeKey', None)
    fieldOptions = {}
    fieldValue, displayValue = GetFieldValue(businessEntity, **configuredData)
    if fieldType == 'SE' or fieldType == 'MS':
        if hasattr(businessEntity, 'get_%s_options' % fieldKey):
            # Get selection option from business entity
            fieldOptions = eval("businessEntity.get_%s_options()" % fieldKey)
        elif storeKey and storeType == 'Customized' or storeType == 'Activity':
            if hasattr(businessEntity, 'orderModel'):
                # Get options from OrderExtSelectionFieldType by storeKey
                for option in businessEntity.orderModel.type.orderextselectionfieldtype_set.filter(fieldKey=storeKey):
                    fieldOptions[option.key] = option.description
    return fieldValue, displayValue, fieldOptions


def AddObjectIdToHistory(request, context, objectId, type):
    uid = request.session['up']['userloginid']
    userLogin = UserLogin.objects.get(id=uid)
    allViewHistory = UserViewHistory.objects.filter(userlogin=userLogin).order_by('-viewedAt')
    viewHistory = allViewHistory.filter(objectId=objectId, type=type)
    if not viewHistory:
        uvh = UserViewHistory()
        uvh.userlogin = userLogin
        uvh.objectId = objectId
        uvh.type = type
        uvh.viewedAt = datetime.datetime.now()
        uvh.save()
    else:
        viewHistory[0].viewedAt = datetime.datetime.now()
        viewHistory[0].save()
    # keep 5 recent items
    if allViewHistory.count() > 5:
        for o in allViewHistory[5:]:
            o.delete()


def GetChangeHistoryRec(id, field, newValue, oldValue, updatedBy):
    record = {}
    record['id'] = id
    record['field'] = field
    record['newValue'] = newValue
    record['oldValue'] = oldValue
    record['updatedBy'] = updatedBy
    return record


def AddEntityLock(objectId, type, bpId):
    lock = LockTable()
    lock.objectId = objectId
    lock.tableType = type
    lock.lockedBy = bpId
    lock.save()


def GetEntityLock(objectId, type, lockedByBpId):
    locks = LockTable.objects.filter(Q(objectId=objectId), Q(tableType=type), ~Q(lockedBy=lockedByBpId))
    if locks:
        return locks[0]
    else:
        return None


def DeleteEntityLock(objectId, type, lockedBpId):
    LockTable.objects.filter(objectId=objectId, tableType=type, lockedBy=lockedBpId).delete()


def GetElasticSearchData(hostString, index, docType, body=None, params={'search_type': 'count'}):
    """
    This method return all data from elastic search by given index, document type
    :param hostString: Host string, e.g '127.0.0.1:9200;192.168.1.4:9200'
    :param index: Index name
    :param docType: Document type
    :return: data array
    """
    hosts = []
    servers = hostString.split(';')
    for server in servers:
        s = server.split(':')
        host = {}
        host['host'] = s[0]
        host['port'] = int(s[1])
        hosts.append(host)

    es = Elasticsearch(hosts)
    try:
        if body is None:
            result = \
                es.search(index=index, doc_type=docType, body={"query": {"match_all": {}}}, params=params)['hits'][
                    'hits']
        else:
            result = \
                es.search(index=index, doc_type=docType, body=body, params=params)
        return result
    except Exception, e:
        log.error('Elasticsearch connection error %s', e)
        return None


def GetAllEmployeeUnderOrg(orgBp):
    """
    This method get all employees (type IN) recursively under a certain org
    :param orgBp:
    :return: employee bp object list
    """
    employees = []
    subBPRitem = [bpr for bpr in BPRelation.objects.filter(bpA=orgBp, relation="BL")]
    if subBPRitem:
        for item in subBPRitem:
            if item.bpB.type.key == 'OR':
                employees.extend(GetAllEmployeeUnderOrg(item.bpB))
            elif item.bpB.type.key == 'IN':
                if item.bpB not in employees:
                    employees.append(item.bpB)
    return employees


def GetOrderStageStatistics(orderId, stageKeyArray):
    """
    This method get order stage statistics by the stage key array
    :param orderId:
    :param stageKeyArray:
    :return:
    """
    # stageDaysList is ordered by stage from 00001 to 00005
    stageDaysList = []
    # Initial start date is the creation date
    currentOrder = Order.objects.get(id=orderId)
    sDate = orderCreatedAt = currentOrder.createdAt

    for i in range(5):
        stageStatistic = {}
        stageStatistic['visible'] = True
        stageStatistic['daysDiff'] = None
        stageStatistic['cssClass'] = 'danger'
        stageStatistic['icon'] = 'remove-circle'
        stageDaysList.append(stageStatistic)

    # Cache order stage change log
    orderStageChangeHistory = ChangeHistory.objects.filter(objectId=orderId, type='Order',
                                                           objectField='stage').order_by('-updatedAt')
    if not orderStageChangeHistory:
        # Check current stage
        currentStage = currentOrder.ordercustomized.stage
        index = stageKeyArray.index(currentStage)
        if index > 4:
            # Alread online(Stage 00006), render stage 00005
            index = 4
            # Order completed
            isDone = True
            # Completion date is last updated date
            eDate = currentOrder.updatedAt
        else:
            # Not completed, working in progress
            isDone = False
            # Calculate date til now
            eDate = datetime.datetime.now()
        stageStatistic = stageDaysList[index]
        eDate = eDate.replace(tzinfo=None)
        sDate = sDate.replace(tzinfo=None)
        daysDiff = (eDate - sDate).days
        stageStatistic['daysDiff'] = daysDiff
        stageStatistic['cssClass'] = GetClassForStageDays(daysDiff)
        if isDone:
            stageStatistic['icon'] = 'thumbs-up'
        else:
            stageStatistic['icon'] = 'play'
    else:
        # Loop for each stage, started from 00002
        for i in range(1, 6):
            print stageKeyArray[i]
            if i == 1:
                # For the first one, set default sDate eDate = created date
                sDate = eDate = orderCreatedAt
            else:
                # Start from second one, sDate is the previous eDate
                sDate = eDate
            # Get changed date of giving stage (changed to stage)
            changedAt = GetOrderStageChangedAt(orderId, stageKeyArray[i], orderStageChangeHistory)
            if changedAt:
                # New eDate is changed date
                eDate = changedAt
            else:
                # No record found, continue to next one
                continue
            # Calculate date difference
            eDate = eDate.replace(tzinfo=None)
            sDate = sDate.replace(tzinfo=None)
            daysDiff = (eDate - sDate).days
            if daysDiff < 0:
                # Date difference is negative, continue to next stage and reset eDate as sDate
                eDate = sDate
                continue
            # print '%s %s %s' % (stageKeyArray[i], daysDiff, eDate)
            # Fill the result list
            stageStatistic = stageDaysList[i - 1]
            stageStatistic['daysDiff'] = daysDiff
            stageStatistic['cssClass'] = GetClassForStageDays(daysDiff)
            stageStatistic['endDatetime'] = eDate
            stageStatistic['icon'] = 'thumbs-up'
    # Find last valid stage reversely, and hide empty ones
    lastValidChangeIdx = None
    for stageStatistic in stageDaysList[::-1]:
        daysDiff = stageStatistic.get('daysDiff', None)
        if daysDiff is not None:
            # Mark the last valid one index
            lastValidChangeIdx = stageDaysList.index(stageStatistic)
            break
        else:
            # Hide this stage data so that not to be dislayed
            stageStatistic['visible'] = False
    # Adding date difference from now to current stage
    if lastValidChangeIdx is not None and lastValidChangeIdx < len(stageDaysList) - 1:
        lasValidStageStatistic = stageDaysList[lastValidChangeIdx]
        stageStatistic = stageDaysList[lastValidChangeIdx + 1]
        sDate = lasValidStageStatistic.get('endDatetime', None)
        if sDate:
            # Calculate date difference
            eDate = datetime.datetime.now()
            eDate = eDate.replace(tzinfo=None)
            sDate = sDate.replace(tzinfo=None)
            daysDiff = (eDate - sDate).days
            stageStatistic['daysDiff'] = daysDiff
            stageStatistic['cssClass'] = GetClassForStageDays(daysDiff)
            stageStatistic['icon'] = 'play'
            stageStatistic['visible'] = True
    # Reset label for those None daysDiff
    for stageStatistic in stageDaysList:
        if stageStatistic['daysDiff'] is None:
            stageStatistic['daysDiff'] = ''
    # Return result
    return stageDaysList


def GetClassForStageDays(days):
    cssClass = ''
    successDays = SystemConfiguration.objects.filter(key='successDays')
    if successDays:
        successDays = int(successDays[0].value1)
    else:
        successDays = 10
    warningDays = SystemConfiguration.objects.filter(key='warningDays')
    if warningDays:
        warningDays = int(warningDays[0].value1)
    else:
        warningDays = 15
    if days >= 0 and days < successDays:
        cssClass = 'success'
    elif days >= successDays and days < warningDays:
        cssClass = 'warning'
    else:
        cssClass = 'danger'
    return cssClass


def GetOrderStageChangedAtByStagePair(orderId, stageFrom, stageTo, changeHistoryQs=None):
    if changeHistoryQs:
        changeHistory = changeHistoryQs.filter(objectId=orderId, type='Order', objectField='stage',
                                               oldKeyValue=stageFrom,
                                               newKeyValue=stageTo).order_by(
            '-updatedAt')
    else:
        changeHistory = ChangeHistory.objects.filter(objectId=orderId, type='Order', objectField='stage',
                                                     oldKeyValue=stageFrom,
                                                     newKeyValue=stageTo).order_by(
            '-updatedAt')
    if changeHistory:
        return changeHistory[0].updatedAt
    else:
        return None


def GetOrderStageChangedAt(orderId, stageKey, changeHistoryQs=None):
    """
    This method get the order stage change the time
    :param orderId:
    :param stageKey:
    :return:
    """
    if changeHistoryQs:
        changeHistory = changeHistoryQs.filter(objectId=orderId, type='Order', objectField='stage',
                                               newKeyValue=stageKey).order_by(
            '-updatedAt')
    else:
        changeHistory = ChangeHistory.objects.filter(objectId=orderId, type='Order', objectField='stage',
                                                     newKeyValue=stageKey).order_by(
            '-updatedAt')
    if changeHistory:
        return changeHistory[0].updatedAt
    else:
        return None


def GetSalesmanStageData(salesman):
    """
    Get statistics for a certain salesman
    :param salesman:
    :return: a turple contains order overall data and a list of each order's statistics
    """
    result = []
    # Temporarily hardcode stage here, since it will not change
    # 触达，意向，资质，山航签约，签约，上线
    stageArray = ['00001', '00002', '00003', '00004', '00005', '00006']
    # Get all sales order by the person
    saleOrders = Order.objects.filter(deleteFlag=False, type='SA01', orderpf__pf='00003', orderpf__bp=salesman)
    # Total count
    totalCount = saleOrders.count()
    # Pending count, status E0005 搁置
    pendingCount = saleOrders.filter(status__key='E0005').count()
    # Online count, stage 00006 上线
    onlineCount = saleOrders.filter(ordercustomized__stage='00006').count()
    # Get current month
    today = datetime.datetime.now().date()
    thisMonth = datetime.datetime(today.year, today.month, 1)
    # Get new orders created this month
    newOfMonthCount = saleOrders.filter(createdAt__gte=thisMonth).count()
    # Set rate
    salesmanData = {}
    if totalCount != 0:
        pendingRate = "%d" % ((float(pendingCount) / float(totalCount)) * 100)
        onlineRate = "%d" % ((float(onlineCount) / float(totalCount)) * 100)
    else:
        pendingRate = 0
        onlineRate = 0
    salesmanData['pendingRate'] = pendingRate
    salesmanData['onlineRate'] = onlineRate
    salesmanData['totalCount'] = totalCount
    salesmanData['pendingCount'] = pendingCount
    salesmanData['onlineCount'] = onlineCount
    salesmanData['newOfMonthCount'] = newOfMonthCount

    nonPendingOrders = saleOrders.filter(~Q(status__key='E0005'))
    for order in nonPendingOrders:
        # Get statistics for each order of this salesman
        stages = GetOrderStageStatistics(order.id, stageArray)
        resultDic = {}
        resultDic['desc'] = order.description
        resultDic['id'] = order.id
        resultDic['statistic'] = stages
        result.append(resultDic)
    return (salesmanData, result)


def GetOrgSalesmanStageData(salesorg):
    result = []
    salesmanRel = BPRelation.objects.filter(bpA=salesorg, relation='BL')
    for salesman in salesmanRel:
        resultDic = {}
        resultDic['desc'] = salesman.bpB.displayName()
        resultDic['id'] = salesman.bpB.id
        resultDic['statistic'] = GetSalesmanStageData(salesman.bpB)
        result.append(resultDic)
    return result


def GetSDSalesmanStageData(salesorg):
    """
    Get the statistics by the sales organization/area
    :param salesorg:
    :return:
    """
    result = []
    # Find out all salesman belong to this organization/area
    salesmanRel = BPRelation.objects.filter(bpA=salesorg, relation='BL')
    for salesman in salesmanRel:
        # Get statistics by each salesman
        resultDic = {}
        resultDic['desc'] = salesman.bpB.displayName()
        resultDic['id'] = salesman.bpB.id
        (resultDic['salesmanstatistic'], resultDic['recordstatistic']) = GetSalesmanStageData(salesman.bpB)
        result.append(resultDic)
    return result


def GetSalesStageData():
    """
    Get the Sales Department statistics
    :return: statistics list, format as
    [
      {
        'statistic': [
          {
            'recordstatistic': [
              {
                'statistic': [
                  {'daysDiff': 46, 'endDatetime': datetime.datetime(2016, 1, 3, 8, 40, 29, tzinfo=<UTC>), 'visible': True, 'endStage': '00002', 'cssClass': 'danger', 'icon': 'ok-sign'},
                  {'daysDiff': 3, 'visible': True, 'cssClass': 'success', 'icon': 'exclamation-sign', 'endStage': '00003'},
                  {'daysDiff': '', 'visible': False, 'cssClass': 'danger', 'icon': 'remove-circle', 'endStage': '00004'},
                  {'daysDiff': '', 'visible': False, 'cssClass': 'danger', 'icon': 'remove-circle', 'endStage': '00005'},
                  {'daysDiff': '', 'visible': False, 'cssClass': 'danger', 'icon': 'remove-circle', 'endStage': '00006'}],
                'id': 230L,    // Order id
                'desc': u'dt'  // Order description
              }],
            'salesmanstatistic': {'pendingCount': 0, 'totalCount': 1, 'pendingRate': '0', 'newOfMonthCount': 0, 'onlineRate': '0', 'onlineCount': 0},
            'id': 104L,               // Salesman id
            'desc': u'\u5e9e \u78c5'  // Salesman name
          },
          …
        ],
        'id': 186L,  // Organization/Area id
        'desc': u'\u534e\u5317'  // Organization/Area name
      },
      …
    ]
    """
    result = []
    # Get current company
    company = getCurrentCompany()
    # Get sales department, only 1 here and should be existing
    sdRel = BPRelation.objects.filter(bpA=company, relation='SD')
    if sdRel:
        sdRel = sdRel[0]
    # Get the sales organization/area by the department
    orgRel = BPRelation.objects.filter(bpA=sdRel.bpB, relation='BL')
    for org in orgRel:
        # For each organization/area, get the separate statistics
        resultDic = {}
        resultDic['desc'] = org.bpB.displayName()
        resultDic['id'] = org.bpB.id
        resultDic['statistic'] = GetSDSalesmanStageData(org.bpB)
        result.append(resultDic)
    print result
    return result


def GetEmployeeOfDepartment(Department):
    company = getCurrentCompany()
    return BP.objects.filter(asBPB__bpA__asBPB__bpA__asBPB__bpA=company,
                             asBPB__bpA__asBPB__bpA__asBPB__relation=Department).distinct()


def GetElasticSearchBodyForTransactionStatistic(accountNumber, fromDate=None, toDate=None, isShanHang=None,
                                                transactionType=None):
    """
    "2016-01-25T00:00:00+08"
    :param accountNumber:
    :param fromDate:
    :param toDate:
    :return:
    """
    eBody = {
        "fields": [],
        "query": {
            "filtered": {
                "filter": {
                    "and": [
                        {"exists": {"field": "cspDate"}},
                        {"range": {"transactionDate": {}}},
                        {"query": {"match": {"businessType": "AIR_TICKET"}}},
                        {"query": {"match": {"accountNumber": accountNumber}}}
                    ]
                }
            }
        },
        "aggs": {
            "totalTransactionAmount": {"stats": {"field": "transactionAmount"}}
        }
    }
    if fromDate:
        eBody['query']['filtered']['filter']['and'][1]['range']['transactionDate']['gte'] = fromDate
    if toDate:
        eBody['query']['filtered']['filter']['and'][1]['range']['transactionDate']['lt'] = toDate
    if isShanHang:
        eBody['query']['filtered']['filter']['and'].append({"query": {"match": {"ticket.segments.carrier": "SC"}}})
        # eBody['query']['filtered']['filter']['and'].append({"query": {"prefix": {"ticketNumber": "324"}}})
    if transactionType == 'DB':
        eBody['query']['filtered']['filter']['and'].append({"query": {"match": {"transactionType": "DB"}}})
    elif transactionType == 'CR':
        eBody['query']['filtered']['filter']['and'].append({"query": {"match": {"transactionType": "CR"}}})
    return eBody


def GetElasticSearchBodyForAgentTransactionStatistic(agentId, fromDate=None, toDate=None, isShanHang=None,
                                                     transactionType=None):
    """
    "2016-01-25T00:00:00+08"
    :param accountNumber:
    :param fromDate:
    :param toDate:
    :return:
    """
    eBody = {
        "fields": ["accountNumber", "account.accountName"],
        "query": {
            "filtered": {
                "filter": {
                    "and": [
                        {"exists": {"field": "cspDate"}},
                        {"range": {"transactionDate": {}}},
                        {"query": {"match": {"businessType": "AIR_TICKET"}}},
                        {"query": {"match": {"agentId": agentId}}}
                    ]
                }
            }
        },
        "aggs": {
            "accountNumber": {
                "terms": {
                    "field": "accountNumber"
                },
                "aggs": {
                    "totalTransactionAmount": {"stats": {"field": "transactionAmount"}}
                }
            },
        }
    }
    if fromDate:
        eBody['query']['filtered']['filter']['and'][1]['range']['transactionDate']['gte'] = fromDate
    if toDate:
        eBody['query']['filtered']['filter']['and'][1]['range']['transactionDate']['lt'] = toDate
    if isShanHang:
        eBody['query']['filtered']['filter']['and'].append({"query": {"prefix": {"ticketNumber": "324"}}})
    if transactionType == 'DB':
        eBody['query']['filtered']['filter']['and'].append({"query": {"match": {"transactionType": "DB"}}})
    elif transactionType == 'CR':
        eBody['query']['filtered']['filter']['and'].append({"query": {"match": {"transactionType": "CR"}}})
    return eBody


def GetThisWeek(pDate):
    """
    Return nearest Monday
    """
    weekday = pDate.weekday()
    retDate = pDate - datetime.timedelta(days=weekday)
    return datetime.datetime(retDate.year, retDate.month, retDate.day)


def GetThisMonth(pDate):
    """
    Return initial of this month
    """
    return datetime.datetime(pDate.year, pDate.month, 1)


def GetThisSeason(pDate):
    """
    Return initial of this season
    1.1 4.1
    4.1 7.1
    7.1 10.1
    10.1 next 1.1
    """
    month = pDate.month
    if month < 4:
        return datetime.datetime(pDate.year, 1, 1)
    elif month >= 4 and month < 7:
        return datetime.datetime(pDate.year, 4, 1)
    elif month >= 7 and month < 10:
        return datetime.datetime(pDate.year, 7, 1)
    else:
        return datetime.datetime(pDate.year, 10, 1)


def GetThisYear(pDate):
    return datetime.datetime(pDate.year, 1, 1)


def GetAJAXReport(request):
    result = None
    category = request.GET.get('c', None)
    if category == 'salesoverview':
        result = {}
        orgId = request.GET.get('orgId', None)
        stages = OrderExtSelectionFieldType.objects.filter(fieldKey='00003')
        orderIdList = []
        if orgId:
            # Get salesman of each sales org
            salesmanRel = BPRelation.objects.filter(bpA__id=orgId, relation='BL')
            for salesman in salesmanRel:
                # Get order of each salesman
                saleOrders = Order.objects.filter(deleteFlag=False, type='SA01', orderpf__pf='00003',
                                                  orderpf__bp=salesman.bpB)
                for order in saleOrders:
                    orderIdList.append(order.id)
            allOrders = Order.objects.filter(Q(deleteFlag=False), Q(type='SA01'), ~Q(status__key='E0005'),
                                             id__in=orderIdList)
        else:
            # Get all order without the pending one (Status E0005)
            allOrders = Order.objects.filter(Q(deleteFlag=False), Q(type='SA01'), ~Q(status__key='E0005'))
        legend = []
        data = []
        countData = []
        traAmtCountData = []
        amtCountData = []
        highChartFunnelData = []
        for stage in stages:
            orders = allOrders.filter(ordercustomized__stage=stage.key)
            (count, tamt, amt) = getOrderStatics(orders)
            name = stage.description
            legend.append(name)
            data.append({'name': name, 'value': count})
            countData.append(count)
            traAmtCountData.append(tamt)
            amtCountData.append(amt)
            highChartFunnelData.append([name, orders.count()])
        result['legend'] = legend
        result['data'] = data
        result['countData'] = countData
        result['traAmtCountData'] = traAmtCountData
        result['amtCountData'] = amtCountData
        result['highChartFunnelData'] = highChartFunnelData
        # orderList = []
        # for model in allOrders:
        #     # model = WrapSaleLeadOrder(model)
        #     m = {}
        #     m['id'] = model.id
        #     m['desc'] = model.description
        #     # log.info('%s' % type(model))
        #     empResp = model.orderpf_set.filter(pf__key='00003')
        #     if empResp:
        #         empResp = empResp[0]
        #         m['empResp'] = empResp.bp.displayName()
        #     else:
        #         m['empResp'] = ''
        #     # if model.customer.address1:
        #     #     m['district'] = model.customer.address1.district.description
        #     # else:
        #     #     m['district'] = ''
        #     m['travelAmount'] = model.ordercustomized.travelAmount
        #     m['amount'] = model.ordercustomized.amount
        #     m['goLiveDate'] = str(model.ordercustomized.goLiveDate)
        #     # m['priority'] = model.priority.description
        #     # m['status'] = model.status.description
        #     # m['channel'] = model.channel.name1
        #     channel = model.orderpf_set.filter(pf__key='00002')
        #     if channel:
        #         channel = channel[0]
        #         m['channel'] = channel.bp.displayName()
        #     else:
        #         m['channel'] = ''
        #     m['stage'] = model.ordercustomized.displayStage()
        #     texts = model.ordertext_set.all().order_by('-createdAt')
        #     if texts:
        #         m['text'] = texts[0].content
        #     else:
        #         m['text'] = ''
        #     orderList.append(m)
        # result['orderList'] = json.dumps(orderList)
        opt = getEChartOptionTemplate()
        opt['tooltip']['formatter'] = "{b} : {c}"
        opt['legend'] = {'data': [getPhrase(request, 'order', 'travelAmount'), getPhrase(request, 'order', 'amount')]}
        opt['series'][0]['name'] = getPhrase(request, 'order', 'travelAmount')
        opt['series'][0]['type'] = 'bar'
        opt['series'][0]['data'] = traAmtCountData
        opt['series'].append({})
        opt['series'][1]['name'] = getPhrase(request, 'order', 'amount')
        opt['series'][1]['type'] = 'bar'
        opt['series'][1]['data'] = amtCountData
        opt['grid'] = {}
        opt['grid']['width'] = '80%'
        opt['grid']['height'] = '80%'
        opt['grid']['x'] = '15%'
        opt['grid']['y'] = '10%'
        opt['grid']['x2'] = '90%'
        opt['grid']['y2'] = '90%'
        opt['xAxis'] = [{'type': 'category', 'data': legend}]
        opt['yAxis'] = [{'type': 'value'}]
        result['stackOpt'] = json.dumps(opt)

    elif category == 'tmcoverview':
        result = {}
        # All TMC Stack/Charts
        # Travel amount sum of all golive customer group by TMC
        data = []
        eIndexName = SystemConfiguration.objects.filter(key='ELASTICINDEXNAME')
        eServer = SystemConfiguration.objects.filter(key='ELASTICSERVER')
        if eIndexName and eServer:
            eIndexName = eIndexName[0].value1
            eServer = eServer[0].value1
            eResult = GetElasticSearchData(eServer, eIndexName, "travelAmountAllArea", None, {})
            if eResult:
                opt = getEChartOptionTemplate()
                tmcData = {}
                for row in eResult:
                    rec = row['_source']
                    tmc = tmcData.get(rec['agentName'], None)
                    if not tmc:
                        tmc = {}
                        tmcData[rec['agentName']] = tmc
                        tmc['uatp'] = 0
                        tmc['nonuatp'] = 0
                    if rec['paymentType'] == 'UATP':
                        tmc['uatp'] = rec['totalTransactionAmount']
                    else:
                        tmc['nonuatp'] = rec['totalTransactionAmount']
                result['tmcData'] = json.dumps(tmcData)

                opt = getEChartOptionTemplate()
                for k, v in tmcData.items():
                    amount = float(v['uatp']) + float(v['nonuatp'])
                    data.append({'name': k, 'value': str(amount)})

                opt = getEChartOptionTemplate()
                opt['tooltip']['formatter'] = "{b}<br>{c}<br>({d}%)"
                opt['title']['text'] = ''
                # opt['legend']['data'] = legend
                opt['series'][0]['name'] = 'name'
                opt['series'][0]['data'] = data
                result['goLiveTmcTAmtPieOpt'] = json.dumps(opt)
                # TMC Payment Type Stack
                uatpData = []
                nonuatpData = []
                legend = []
                splitAt = 7
                for k, tmc in tmcData.items():
                    if len(k) > splitAt:
                        name = ''.join([k[0:splitAt], "\n", k[splitAt:]])
                    else:
                        name = k
                    legend.append(name)
                    u = tmc.get('uatp', 0)
                    nu = tmc.get('nonuatp', 0)
                    uatpData.append(u)
                    nonuatpData.append(nu)
                sopt = getEChartOptionTemplate()
                sopt['tooltip']['formatter'] = "{b} : {c}"
                puatp = getPhrase(request, 'order', 'UATP')
                pnonuatp = getPhrase(request, 'order', 'NONUATP')
                sopt['legend']['data'] = [puatp, pnonuatp]
                sopt['series'][0]['name'] = puatp
                sopt['series'][0]['type'] = 'bar'
                sopt['series'][0]['data'] = uatpData
                sopt['series'].append({})
                sopt['series'][1]['name'] = pnonuatp
                sopt['series'][1]['type'] = 'bar'
                sopt['series'][1]['data'] = nonuatpData
                sopt['xAxis'] = [{'type': 'category', 'data': legend, 'axisLabel': {'interval': 0, 'rotate': 0}}]
                sopt['yAxis'] = [{'type': 'value'}]
                sopt['title']['text'] = ''
                sopt['title']['x'] = 'center'
                sopt['grid'] = {'x': 100, 'x2': 0, 'y2': 50}
                result['goLiveTmcTAmtPmtStackOpt'] = json.dumps(sopt)
    elif category == 'corpstructview':
        result = {}
        sopt = getEChartOptionTemplate()
        rels = ['SD', 'OP', 'FI', 'HR', 'PD']
        company = getCurrentCompany()
        node = {'name': company.displayName(), 'value': '', 'children': []}
        for rel in rels:
            bps = BPRelation.objects.filter(bpA=company, relation=rel, valid=True)
            for bp in bps:
                subNode = {'name': bp.bpB.displayName(), 'value': '', 'children': []}
                getBPRelForEChartTree(subNode['children'], bp, 'BL')
                subNode['symbol'] = 'image:///salesstatic/customized/img/dep_%s.png' % rel.lower()
                subNode['symbolSize'] = [30, 30]
                node['children'].append(subNode)
        sopt['tooltip'] = {
            'trigger': 'item',
            'formatter': "{b}"
        }
        sopt['series'] = [
            {
                'name': u'树图',
                'type': 'tree',
                'orient': 'vertical',
                'rootLocation': {'x': 'center', 'y': 50},
                'nodePadding': 20,
                'layerPadding': 40,
                'symbol': "image:///salesstatic/customized/img/logo.png",
                'symbolSize': [152, 20],
                'itemStyle': {
                    'normal': {
                        'label': {
                            'show': 'true',
                            'formatter': "{a} {b} {c}"
                        },
                        'lineStyle': {
                            'color': '#48b',
                            'shadowColor': '#000',
                            'shadowBlur': 3,
                            'shadowOffsetX': 3,
                            'shadowOffsetY': 5,
                            'type': 'curve'
                        }
                    },
                    'emphasis': {
                        'label': {
                            'show': 'true'
                        }
                    }
                },
                'data': [node]
            }]
        result['structureChart'] = json.dumps(sopt)
    elif category == 'access':
        result = {}
        date = datetime.datetime.now() - datetime.timedelta(days=7)
        opt = getEChartOptionTemplate()
        appList = []
        userList = []
        seriesList = []
        pageApps = AppNavAccess.objects.all().values('pageApp').distinct()
        for pageApp in pageApps:
            appList.append(pageApp['pageApp'])
        userAccessData = {}
        for ul in UserLogin.objects.all():
            groupedResult = AppNavAccess.objects.filter(Q(userLogin=ul), Q(accessedAt__gte=date)).values(
                'pageApp').annotate(sum=Count('id'))
            if not groupedResult:
                continue
            userList.append(ul.userbp.displayName())
            userAccessData[ul.userbp.displayName()] = groupedResult
        for app in appList:
            series = {}
            countDataList = []
            series['name'] = app
            series['type'] = 'bar'
            series['stack'] = 'App'
            for user in userList:
                groupedResult = userAccessData[user]
                for result in groupedResult:
                    if result['pageApp'] == app:
                        countDataList.append(result['sum'])
                        continue
            series['data'] = countDataList
            seriesList.append(series)
        opt['legend'] = {
            'data': appList
        }
        opt['tooltip'] = {
            'trigger': 'axis',
            'axisPointer': {
                'type': 'shadow'
            }}
        opt['xAxis'] = [
            {
                'type': 'category',
                'data': userList
            }
        ]
        opt['yAxis'] = [
            {
                'type': 'value'
            }
        ]
        opt['series'] = seriesList
        result['accessChart'] = json.dumps(opt)
    return result


def GetRandomName(name):
    result = '%s%d%d' % (name, int(time.time()), randint(0, 999999))
    return result


def ConvertNormalStringToHtml(normalString):
    result = normalString
    result = result.replace('<', '&lt;')
    result = result.replace('>', '&gt;')
    result = result.replace('\n', '<br>')
    return result


# Model Service class, used to handle CRUD methods
class BaseModelService(object):
    def __init__(self):
        pass

    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        pass

    def getlist(self, *args, **kwargs):
        pass


class TMCModelService(BaseModelService):
    def get(self, *args, **kwargs):
        super(TMCModelService, self).get(*args, **kwargs)
        request = kwargs.get('request', {})
        bpId = request.POST.get('id', None)
        if bpId:
            model = {}
            bp = BP.objects.get(id=bpId)
            model['name'] = bp.name1
            if bp.address1:
                model['address'] = bp.address1.address1
                model['district'] = bp.address1.district.key
            else:
                model['address'] = ''
                model['district'] = ''
            model['empResp'] = ''
            if hasattr(bp, 'bpcustomized'):
                model['touched'] = bp.bpcustomized.boolAttribute1
                model['signed'] = bp.bpcustomized.boolAttribute2
                model['connected'] = bp.bpcustomized.boolAttribute3
                if bp.bpcustomized.empResp:
                    model['empResp'] = bp.bpcustomized.empResp.id
            else:
                model['touched'] = False
                model['signed'] = False
                model['connected'] = False
            texts = bp.bptext_set.all().order_by('-createdAt')
            if texts:
                logText = ''
                for l in texts:
                    # Build log
                    t = '%s %s %s<br>----------<br>%s' % (
                        l.type.description, l.createdBy.displayName(),
                        timezone.localtime(l.createdAt).strftime('%Y-%m-%d %H:%M:%S'),
                        l.content)
                    logText = '%s%s<br><br>' % (logText, t)
                model['text'] = logText
            return model

    def getlist(self, *args, **kwargs):
        com = getCurrentCompany()
        tmcs = BP.objects.filter(asBPB__bpA=com, asBPB__relation='TM', valid=True).all()
        result = []
        for tmc in tmcs:
            record = {}
            texts = tmc.bptext_set.all().order_by('-createdAt')
            if texts:
                tmc.latestText = texts[0].content
            else:
                tmc.latestText = ''
            record['id'] = tmc.id
            record['name'] = tmc.displayName()
            if tmc.address1 and tmc.address1.district:
                record['district'] = tmc.address1.district.description
            else:
                record['district'] = ''
            record['empResp'] = ''
            record['empRespName'] = ''
            if hasattr(tmc, 'bpcustomized'):
                record['touched'] = tmc.bpcustomized.boolAttribute1
                record['signed'] = tmc.bpcustomized.boolAttribute2
                record['connected'] = tmc.bpcustomized.boolAttribute3
                if tmc.bpcustomized.empResp:
                    record['empResp'] = tmc.bpcustomized.empResp.id
                    record['empRespName'] = tmc.bpcustomized.empResp.displayName()
            else:
                record['touched'] = False
                record['signed'] = False
                record['connected'] = False
            record['text'] = tmc.latestText
            result.append(record)
        return result

    def update(self, *args, **kwargs):
        request = kwargs.get('request', {})
        touched = request.POST.get('touched', False)
        signed = request.POST.get('signed', False)
        connected = request.POST.get('connected', False)
        text = request.POST.get('text', False)
        address = request.POST.get('address', False)
        district = request.POST.get('district', False)
        tmcId = request.POST.get('id', None)
        empResp = request.POST.get('empResp', None)
        if tmcId:
            tmc = BP.objects.get(id=tmcId)
            # log.info('tmc %s' % tmc.bpcustomized)
            bpcust = BPCustomized.objects.filter(bp=tmcId)
            # tmc.get('bpcustomized',None)
            if not bpcust:
                bpcust = BPCustomized()
                tmc.bpcustomized = bpcust
                tmc.save()
            else:
                bpcust = bpcust[0]
            bpcust.boolAttribute1 = bool(touched == 'true') and True or False
            bpcust.boolAttribute2 = bool(signed == 'true') and True or False
            bpcust.boolAttribute3 = bool(connected == 'true') and True or False
            if empResp:
                bpcust.empResp = BP.objects.get(id=empResp)
            bpcust.save()
            if text:
                bpText = BPText()
                bpText.bp = tmc
                bpText.type = BPTextType.objects.get(pk='MEMO')
                bpText.content = text
                bpText.createdBy = getCurrentUserBp(request)
                bpText.save()
            if address or district:
                oldAddress = tmc.address1
                if oldAddress is None:
                    newAddress = Address()
                    newAddress.type = AddressType.objects.get(pk='ST')
                    newAddress.address1 = address
                    if district:
                        newAddress.district = DistrictType.objects.get(pk=district)
                    newAddress.save()
                    tmc.address1 = newAddress
                    tmc.save()
                else:
                    oldAddress.address1 = address
                    if district:
                        oldAddress.district = DistrictType.objects.get(pk=district)
                    oldAddress.save()


class CustomerModelService(BaseModelService):
    def get(self, *args, **kwargs):
        super(CustomerModelService, self).get(*args, **kwargs)
        request = kwargs.get('request', {})
        bpId = request.POST.get('id', None)
        if bpId:
            model = {}
            bp = BP.objects.get(id=bpId)
            model['name'] = bp.name1
            model['address'] = ''
            model['district'] = ''
            model['phone'] = ''
            model['contactPerson'] = ''
            model['legalPerson'] = ''
            model['actualPerson'] = ''
            model['corpStructure'] = ''
            model['corpLicense'] = False
            if hasattr(bp, 'address1'):
                model['address'] = bp.address1.address1
                if bp.address1.district:
                    model['district'] = bp.address1.district.key
                    model['districtName'] = bp.address1.district.description
                model['phone'] = bp.address1.phone1
                model['contactPerson'] = bp.address1.contact1
            if hasattr(bp, 'bpcustomized'):
                model['legalPerson'] = bp.bpcustomized.legalPerson
                model['actualPerson'] = bp.bpcustomized.actualPerson
                model['corpStructure'] = bp.bpcustomized.corpStructure
                if bp.bpcustomized.corpLiscense:
                    model['corpLicense'] = True
                    model['imgData'] = base64.encodestring(bp.bpcustomized.corpLiscense._get_file().read())
                    # model['imgData'] =

            return model

    def update(self, *args, **kwargs):
        request = kwargs.get('request', {})
        bpId = request.POST.get('id', None)
        name = request.POST.get('name', None)
        district = request.POST.get('district', None)
        addressStr = request.POST.get('address', None)
        phone = request.POST.get('phone', None)
        contactPerson = request.POST.get('contactPerson', None)
        legalPerson = request.POST.get('legalPerson', None)
        actualPerson = request.POST.get('actualPerson', None)
        corpStructure = request.POST.get('corpStructure', None)
        if bpId:
            customer = BP.objects.get(id=bpId)
            customer.name1 = name
            if not hasattr(customer, 'address1'):
                address = Address()
                address.save()
                customer.address1 = address
                customer.save()
            address = customer.address1
            address.address1 = addressStr
            address.district = DistrictType.objects.get(key=district)
            address.phone1 = phone
            address.contact1 = contactPerson
            address.save()
            if not hasattr(customer, 'bpcustomized'):
                bpcust = BPCustomized()
                bpcust.bp = customer
                bpcust.save()
                # customer.bpcustomized = bpcust
                # customer.save()
            bpcust = customer.bpcustomized
            bpcust.legalPerson = legalPerson
            bpcust.actualPerson = actualPerson
            bpcust.corpStructure = corpStructure
            bpcust.save()
            customer.save()

    def getlist(self, *args, **kwargs):
        companyBP = getCurrentCompany()
        customers = BP.objects.filter(asBPB__bpA=companyBP, asBPB__relation='C1', valid=True).all()
        result = []
        for customer in customers:
            record = {}
            record['id'] = customer.id
            record['name'] = customer.displayName()
            record['district'] = ''
            record['address'] = ''
            if customer.address1:
                record['address'] = customer.address1.address1
            if customer.address1 and customer.address1.district:
                record['district'] = customer.address1.district.description
            result.append(record)
        return result


class FeedbackModelService(BaseModelService):
    def create(self, *args, **kwargs):
        request = kwargs.get('request', {})
        title = request.POST.get('title', None)
        type = request.POST.get('type', None)
        text = request.POST.get('text', None)
        ul = getCurrentUser(request)
        ufb = UserFeedback()
        ufb.userLogin = ul
        ufb.title = title
        ufb.type = type
        ufb.text = text
        ufb.save()

    def get(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def getlist(self, *args, **kwargs):
        pass


class MessageModelService(BaseModelService):
    def create(self, *args, **kwargs):
        request = kwargs.get('request', {})
        receiverIds = request.POST.getlist('receiverId[]', None)
        for receiverId in receiverIds:
            text = request.POST.get('text', None)
            siteMessage = SiteMessage()
            ul = getCurrentUser(request)
            siteMessage.sender = ul
            siteMessage.receiver = UserLogin.objects.get(id=receiverId)
            siteMessage.sentAt = datetime.datetime.now()
            siteMessage.message = text
            siteMessage.save()

    def get(self, *args, **kwargs):
        request = kwargs.get('request', {})
        messageId = request.POST.get('id', None)
        message = SiteMessage.objects.get(id=messageId)
        record = {}
        record['id'] = message.id
        record['senderId'] = message.sender.id
        record['sender'] = message.sender.userbp.displayName()
        record['message'] = ConvertNormalStringToHtml(message.message)
        record['sentAt'] = timezone.localtime(message.sentAt).strftime('%Y-%m-%d %H:%M:%S')
        return record

    def update(self, *args, **kwargs):
        request = kwargs.get('request', {})
        messageId = request.POST.get('id', None)
        flag = request.POST.get('receiverReadFlag', False)
        deleteFlag = request.POST.get('receiverDeleteFlag', False)
        message = SiteMessage.objects.get(id=messageId)
        message.receiverReadFlag = bool(flag == 'true')
        message.receiverDeleteFlag = bool(deleteFlag == 'true')
        message.save()

    def getlist(self, *args, **kwargs):
        result = []
        request = kwargs.get('request', {})
        ul = getCurrentUser(request)
        messages = SiteMessage.objects.filter(receiver=ul, receiverDeleteFlag=False).order_by("-sentAt")
        for message in messages:
            record = {}
            record['id'] = message.id
            record['sender'] = message.sender.userbp.displayName()
            record['message'] = ConvertNormalStringToHtml(message.message)
            record['sentAt'] = timezone.localtime(message.sentAt).strftime('%Y-%m-%d %H:%M:%S')
            record['receiverReadFlag'] = message.receiverReadFlag
            result.append(record)
        return result


def isSystemInMaintain():
    isMaint = SystemConfiguration.objects.filter(key='MAINT_RUNNING')
    allowedUser = SystemConfiguration.objects.filter(key='MAINT_ALLOWED_USER')
    if isMaint:
        isMaint = isMaint[0].value1
    if allowedUser:
        allowedUser = allowedUser[0].value1
    return (isMaint, allowedUser)


def logAppAccess(user, nav, type=None):
    pageApp = nav.get('pageApp', None)
    pageAction = nav.get('pageAction', None)
    pageParams = nav.get('pageParams', None)
    pageMode = nav.get('pageMode', None)
    appNavAccess = AppNavAccess()
    appNavAccess.userLogin = user
    appNavAccess.pageApp = pageApp
    appNavAccess.pageAction = pageAction
    appNavAccess.pageParams = pageParams
    appNavAccess.pageMode = pageMode
    appNavAccess.save()


def getBPRelForEChartTree(children, bpr, relation):
    bprs = BPRelation.objects.filter(bpA=bpr.bpB, relation=relation, valid=True)
    size = bprs.count()
    for sbpr in bprs:
        node = {'name': sbpr.bpB.displayName(),
                'value': '',
                'symbol': 'emptyTriangle',
                'symbolSize': 40,
                'itemStyle': {
                    'normal': {
                        'label': {'position': 'bottom'},
                        'color': '#fa6900',
                        'borderWidth': 2,
                        'borderColor': '#cc66ff'
                    }
                },
                'children': []}
        children.append(node)
        subSize = getBPRelForEChartTree(node['children'], sbpr, relation)
        if subSize == 0:
            node['symbol'] = 'image:///salesstatic/customized/img/person.png'
            node['symbolSize'] = [30, 30]
        else:
            node['symbol'] = 'image:///salesstatic/customized/img/team.png'
            node['symbolSize'] = [30, 30]
            node['itemStyle'] = {
                'normal': {
                    'label': {
                        'position': 'top'
                    },
                    'color': '#fa6900',
                    'brushType': 'stroke',
                    'borderWidth': 1,
                    'borderColor': '#999966',
                },
                'emphasis': {
                    'borderWidth': 0
                }
            }
    return size
