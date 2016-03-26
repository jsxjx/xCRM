# -*- coding: UTF-8 -*-
from common import *

log.info('view.py initialized')


# BP
class BPAppView(ModelStdView):
    def __init__(self, page=None):
        log.info('BPAppView init')
        ModelStdView.__init__(self, page)

    def initialize(self, request, context):
        bpId = request.session.get('bpId', None)
        bpType = request.session.get('bpType', None)
        if bpId:
            del request.session['bpId']
        if bpType:
            del request.session['bpType']
        super(BPAppView, self).initialize(request, context)

    def search(self, request, context):
        name1 = request.POST.get('name1', None)
        bpRelation = request.POST.get('bpRelation', None)
        log.info('%s %s' % (name1, bpRelation))
        if not name1 and not bpRelation:
            name1 = request.session.get('name1', None)
            bpRelation = request.session.get('bpRelation', None)
        else:
            request.session['name1'] = name1
            request.session['bpRelation'] = bpRelation
        com = getCurrentCompany()
        filter = {}
        if name1:
            filter['name1__icontains'] = name1
        if bpRelation:
            filter['asBPB__bpA'] = com
            filter['asBPB__relation'] = bpRelation
        if filter:
            models = BP.objects.filter(**filter)
        else:
            models = BP.objects.all()
        context.push({'models': models})
        super(BPAppView, self).search(request, context)

    def view(self, request, context):
        bpId = request.POST.get('pageParams', None)
        if bpId:
            request.session['bpId'] = bpId
            model = BP.objects.get(id=bpId)
            request.session['bpType'] = context['bpType'] = model.type.key
            context.push({'model': model})
        super(BPAppView, self).view(request, context)

    def new(self, request, context):
        bpType = request.POST.get('pageParams', None)
        if not bpType:
            self.search(request, context)
            return
        log.info('%s' % bpType)
        request.session['bpType'] = context['bpType'] = bpType
        super(BPAppView, self).new(request, context)

    def edit(self, request, context):
        bpId = request.session['bpId']
        if bpId:
            model = BP.objects.get(id=bpId)
            request.session['bpType'] = context['bpType'] = model.type.key
            context.push({'model': model})
        super(BPAppView, self).edit(request, context)

    def save(self, request, context):
        bpId = request.session.get('bpId', None)
        bpType = request.session.get('bpType', None)
        log.info('id:%s type:%s' % (bpId, bpType))
        if bpId:
            # Save existing BP records
            model = BP.objects.get(id=bpId)
            fn = request.POST.get('firstName', None)
            mn = request.POST.get('middleName', None)
            ln = request.POST.get('lastName', None)
            name1 = request.POST.get('name1', None)
            address1 = request.POST.get('address', None)
            district = request.POST.get('district', None)
            if address1 or district:
                # Check if address exists
                address = model.address1
                if address:
                    # Modify address
                    address.address1 = address1
                    address.district = DistrictType.objects.get(pk=district)
                    address.save()
                else:
                    # Create new address
                    address = Address()
                    address.type = AddressType.objects.get(pk='ST')
                    address.address1 = address1
                    address.district = DistrictType.objects.get(pk=district)
                    address.save()
                    model.address1 = address

            if bpType == 'IN':
                model.firstName = fn
                model.middleName = mn
                model.lastName = ln
                model.save()
            if bpType == 'CO':
                model.name1 = name1
                model.save()
            request.session['bpType'] = context['bpType'] = model.type.key
            context.push({'model': model})
        else:
            # Create new BP record
            request.session['bpType'] = context['bpType'] = bpType
            if bpType == 'IN':
                fn = request.POST.get('firstName', None)
                mn = request.POST.get('middleName', None)
                ln = request.POST.get('lastName', None)
                asEmp = request.POST.get('asEmp', None)
                address1 = request.POST.get('address', None)
                district = request.POST.get('district', None)
                if not fn and not mn and not ln:
                    context['messagebar'] = [{'type': 'error', 'content': 'Names should not be empty'}]
                    return
                newBP = BP()
                newBP.type = BPType.objects.get(pk='IN')
                newBP.firstName = fn
                newBP.middleName = mn
                newBP.lastName = ln

                # Create new address
                address = Address()
                address.type = AddressType.objects.get(pk='ST')
                address.address1 = address1
                address.district = DistrictType.objects.get(pk=district)
                address.save()
                newBP.address1 = address
                newBP.save()

                if asEmp:
                    com = getCurrentCompany()
                    bpr = BPRelation()
                    bpr.bpA = com
                    bpr.bpB = newBP
                    bpr.relation = BPRelType.objects.get(pk='A1')
                    bpr.save()
                request.session['bpId'] = newBP.id
                model = BP.objects.get(id=newBP.id)
                context.push({'model': model})
                super(BPAppView, self).view(request, context)
                return
            if bpType == 'CO':
                name1 = request.POST.get('name1', None)
                relation = request.POST.get('relation', None)
                if not name1:
                    context['messagebar'] = [{'type': 'error', 'content': 'Names should not be empty'}]
                    return
                newBP = BP()
                newBP.type = BPType.objects.get(pk='CO')
                newBP.name1 = name1
                newBP.save()
                com = getCurrentCompany()
                bpr = BPRelation()
                bpr.bpA = com
                bpr.bpB = newBP
                bpr.relation = BPRelType.objects.get(pk=relation)
                bpr.save()
                request.session['bpId'] = newBP.id
                model = BP.objects.get(id=newBP.id)
                context.push({'model': model})
                super(BPAppView, self).view(request, context)
                return

        super(BPAppView, self).save(request, context)

    def cancel(self, request, context):
        bpId = request.session.get('bpId', None)
        if bpId:
            model = BP.objects.get(id=bpId)
            context.push({'model': model})
            request.session['bpType'] = context['bpType'] = model.type.key
            super(BPAppView, self).cancel(request, context)
        else:
            super(BPAppView, self).initialize(request, context)

    def leave(self, request, context):
        pass


class StepView(object):
    def __init__(self, page=None):
        self.page = page

    def initialize(self, request, context):
        log.info('Initialized')
        context['nav']['pageStatus'] = 'step1'
        stepViewContext = StepViewContext()

        # stepViewContext getContext(request, 'StepViewContext')
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp

        orders = Order.objects.filter(type='SA01', deleteFlag=False, orderpf__pf__key='00003', orderpf__bp=userBp)
        stepViewContext.myOrders = orders

        options = ''.join([('<option value="%s">%s</option>' % (
            order.id, order.description)) for order in orders])
        context['myOrders'] = orders
        context['myOrdersOptions'] = options
        setContext(request, 'StepViewContext', stepViewContext)

    def step1(self, request, context):
        log.info('step1')
        context['nav']['pageStatus'] = 'step1'
        stepViewContext = getContext(request, 'StepViewContext')
        uid = request.session['up']['userloginid']
        userBp = UserLogin.objects.get(id=uid).userbp
        orders = Order.objects.filter(type='SA01', deleteFlag=False, orderpf__pf__key='00003', orderpf__bp=userBp)
        stepViewContext.myOrders = orders
        selectedOrderId = stepViewContext.selectedOrderId
        if selectedOrderId is None:
            options = ''.join([('<option value="%s">%s</option>' % (
                order.id, order.description)) for order in orders])
        else:
            options = ''.join([('<option value="%s" %s>%s</option>' % (
                order.id, bool(str(order.id) == str(selectedOrderId)) and """ selected ="selected" """ or "",
                order.description)) for order in
                               orders])
        context['myOrders'] = orders
        context['myOrdersOptions'] = options
        setContext(request, 'StepViewContext', stepViewContext)

    def step2(self, request, context):
        log.info('step2')
        stepViewContext = getContext(request, 'StepViewContext')
        context['nav']['pageStatus'] = 'step2'
        selectedOrderId = request.POST.get('selectedOrderId', None)
        if selectedOrderId is None:
            selectedOrderId = stepViewContext.selectedOrderId

        print 'selectedOrderId: %s' % selectedOrderId

        stepViewContext.selectedOrderId = selectedOrderId
        stepViewContext.selectedOrder = stepViewContext.myOrders.get(id=selectedOrderId)
        setContext(request, 'StepViewContext', stepViewContext)
        context['selectedOrder'] = stepViewContext.selectedOrder

    def step3(self, request, context):
        log.info('step3')
        context['nav']['pageStatus'] = 'step3'
        stepViewContext = getContext(request, 'StepViewContext')
        context['selectedOrder'] = stepViewContext.selectedOrder

    def leave(self, request, context):
        pass


# class StdApp:
#     def __init__(self):
#         self.view = None
#         self.name = None
#         self.statusPageMap={
#             'S1':'search',
#             'S2':'search',
#             'S3':'detail',
#             'S4':'edit',
#             'S5':'new'
#         }
#     def handle(self, request, context):
#         """
#         This method handles actions for this app
#         :param request: django request
#         :param context: django context
#         :return: page name or dictionary object for actions request
#         App navigation rule
#         Status  Action      Status  PageStatus  Page
#         init    <init>      S1      search      Search Page
#         S1      search      S2      search      Search Page with result
#         S2      search      S2      search      Search Page with result
#         S2      new         S5      new         Edit Page(new)
#         S2      view        S3      detail      Detail Page
#         S3      back        S2      back        Search Page with result
#         S3      back'
#         S3      edit        S4      edit        Edit Page
#         S4      cancel      S3      detail      Detail Page
#         S4      save        S3      detail      Detail Page
#         S4      save(fail)  S4      edit        Edit Page
#         S5      cancel      S2      search      Search Page
#         S5      save        S3      detail      Detail Page
#         S5      save(fail)  S5      new         Edit Page(new)
#         """
#         action = context['nav']['pageAction']
#         result = None
#         appContext = getContext(request,appCtxName)
#         if not appContext or action == '':
#             appContext= AppContext()
#             appContext.status = 'S1'
#             setContext(request,appCtxName, appContext)
#             result = self.view.initialize(request, context)
#         elif appContext and action == 'view':
#             appContext.status = 'S3'
#             setContext(request, appCtxName, appContext)
#             result = self.view.view(request, context)
#         elif (appContext.status == 'S1' or appContext.status == 'S2') and action == 'search':
#             appContext.status = 'S2'
#             setContext(request, appCtxName, appContext)
#             result = self.view.search(request, context)
#         elif (appContext.status == 'S1' or appContext.status == 'S2') and action == 'new':
#             appContext.status = 'S5'
#             setContext(request, appCtxName, appContext)
#             result = self.view.new(request, context)
#         elif appContext.status == 'S2' and action == 'view':
#             appContext.status = 'S3'
#             setContext(request, appCtxName, appContext)
#             result = self.view.view(request, context)
#         elif appContext.status == 'S3' and action == 'back':
#             appContext.status = 'S2'
#             setContext(request, appCtxName, appContext)
#             result = self.view.back(request, context)
#         elif appContext.status == 'S3' and action == 'edit':
#             appContext.status = 'S4'
#             setContext(request, appCtxName, appContext)
#             result = self.view.edit(request, context)
#         elif appContext.status == 'S4' and action == 'cancel':
#             appContext.status = 'S3'
#             setContext(request, appCtxName, appContext)
#             result = self.view.cancel(request, context)
#         elif appContext.status == 'S4' and action == 'save':
#             result = self.view.save(request, context)
#             if result:
#                 appContext.status = 'S3'
#             else:
#                 appContext.status = 'S4'
#             setContext(request, appCtxName, appContext)
#         elif appContext.status == 'S5' and action == 'cancel':
#             appContext.status = 'S2'
#             setContext(request, appCtxName, appContext)
#             result = self.view.cancel(request, context)
#         elif appContext.status == 'S5' and action == 'save':
#             result = self.view.cancel(request, context)
#             if result:
#                 appContext.status = 'S3'
#             else:
#                 appContext.status = 'S5'
#             appContext.status = result
#             setContext(request, appCtxName, appContext)
#         elif action == 'xlsoutput':
#             result = self.view.xlsoutput(request, context)
#         if result and (isinstance(result, HttpResponse) or type(result) == dict):
#             return result
#         else:
#             context['nav']['pageStatus'] = self.statusPageMap[appContext.status]
#             return self.view.page
#     def leave(self, request, context):
#         if self.view and hasattr(self.view,'leave'):
#             self.view.leave(request, context)


# Base Application class, an application is a business function and handles
# user operations on page
# The application is triggered by javascript on html
# I.e toNav('<app name>', '<app action>', <app parameter>, <app mode>)
class App:
    def __init__(self):
        self.view = None
        self.name = None

    def handle(self, request, context):
        action = context['nav']['pageAction']
        result = None
        if action == '':
            back = request.session.get('back', None)
            if back:
                del request.session['back']
            result = self.view.initialize(request, context)
        elif action == 'search':
            result = self.view.search(request, context)
        elif action == 'back':
            navPath = request.session.get('navPath', None)
            if len(navPath) > 2:
                originNav = navPath[-3]
                del navPath[-2:]
                request.session['navPath'] = navPath
                preAction = originNav.get('pageAction', None)
                if preAction == 'search':
                    result = self.view.back(request, context)
                else:
                    result = originNav
        elif action == 'view':
            result = self.view.view(request, context)
        elif action == 'edit':
            result = self.view.edit(request, context)
        elif action == 'new':
            result = self.view.new(request, context)
        elif action == 'save':
            result = self.view.save(request, context)
        elif action == 'cancel':
            navPath = request.session.get('navPath', None)
            if len(navPath) > 2:
                del navPath[-2:]
            result = self.view.cancel(request, context)
        elif action == 'upload':
            result = self.view.upload(request, context)
        elif action == 'download':
            result = self.view.download(request, context)
        elif action == 'deletefile':
            result = self.view.deletefile(request, context)
        elif action == 'xlsoutput':
            result = self.view.xlsoutput(request, context)
        elif action == 'createFollowUp':
            # Remove last navigation path of editing status
            # In order to allow back to previous order
            navPath = request.session.get('navPath', None)
            del navPath[-1]
            request.session['navPath'] = navPath
            result = self.view.createFollowUp(request, context)
        if result and (isinstance(result, HttpResponse) or type(result) == dict):
            return result
        else:
            return self.view.page

    def leave(self, request, context):
        self.view.leave(request, context)


class StepBasedApp:
    def __init__(self):
        self.view = None
        self.name = None

    def handle(self, request, context):
        action = context['nav']['pageAction']
        result = None
        if action == '':
            back = request.session.get('back', None)
            if back:
                del request.session['back']
            result = self.view.initialize(request, context)
        elif action == 'back':
            navPath = request.session.get('navPath', None)
            if len(navPath) > 2:
                originNav = navPath[-3]
                del navPath[-2:]
                request.session['navPath'] = navPath
                preAction = originNav.get('pageAction', None)
                if preAction == 'search':
                    result = self.view.back(request, context)
                else:
                    result = originNav
        elif action == 'step1':
            result = self.view.step1(request, context)
            pass
        elif action == 'step2':
            result = self.view.step2(request, context)
            pass
        elif action == 'step3':
            result = self.view.step3(request, context)
            pass
        if result and (isinstance(result, HttpResponse) or type(result) == dict):
            return result
        else:
            return self.view.page

    def leave(self, request, context):
        self.view.leave(request, context)


class CalendarApp:
    def __init__(self):
        self.view = 'crm/calendar.html'

    def handle(self, request, context):
        action = context['nav']['pageAction']
        result = None
        if action == '':
            # Initial, get all events
            context['today'] = datetime.datetime.today().strftime('%Y-%m-%d')
        elif action == 'page':
            return 'crm/calendarItem.html'
        return self.view

    def leave(self, request, context):
        pass


class CreateLeadApp:
    def __init__(self):
        self.view = 'crm/createLead.html'

    def handle(self, request, context):
        action = request.POST.get('pageAction', '')
        if action == '':
            form = CustomerForm(initial={'name1': ''})
            context['form'] = form
            context['nav']['pageStatus'] = 'step1'
        if action == 'search':
            ctx = {}
            context['nav']['pageStatus'] = 'step1'
            form = CustomerForm(request.POST)
            context['form'] = form
            customerName = request.POST.get('name1', None)
            # district = request.POST.get('district',None)
            # if not customerName or not district:
            if not customerName:
                ctx['messagebar'] = [{'type': 'error', 'content': getPhrase(request, 'g_default', 'errNoCustName')}]
                context.push(ctx)
                return self.view

            # Search customer
            company = BP.objects.filter(type='ZZ')[0]
            # customers = [bpr.bpB for bpr in BPRelation.objects.filter(relation='C1',bpA=company,bpB__name1__icontains=customerName,bpB__address1__district=district)]
            customers = BP.objects.filter(valid=True, asBPB__bpA=company, asBPB__relation='C1',
                                          name1__icontains=customerName)
            context.push({'customers': customers})
            context['allowCreate'] = True
            return self.view
        if action == 'createBP':
            if request.session.get('existBP', False):
                log.info('remove customerid %s' % request.session['existBP'])
                del request.session['existBP']
            form = CustomerForm(request.POST)
            if form.is_valid():
                customerName = form.cleaned_data['name1']
                # district = form.cleaned_data['district']
                # log.info('%s %s' % (customerName,district))
                context['customerName'] = customerName
                # context['districtDesc'] = DistrictType.objects.get(pk=district).description
                request.session['newCustomer'] = {
                    'name1': customerName
                    # 'district':district
                }
                form = OrderForm(initial={'description': ''})
                context['form'] = form
            context['nav']['pageStatus'] = 'step2'
        if action == 'existBP':
            customerid = request.POST.get('pageParams', None)
            if customerid:
                bp = BP.objects.get(id=customerid)
                context['customerName'] = bp.name1
                add = bp.address1
                if add:
                    context['districtDesc'] = add.district.description
                else:
                    context['districtDesc'] = ''
                request.session['newCustomer'] = {
                    'name1': bp.name1
                    # 'district':bp.address1.district.key
                }
                if add:
                    request.session['newCustomer']['district'] = add.district.key
                form = OrderForm(initial={'description': ''})
                context['form'] = form
                request.session['existBP'] = customerid
                context['nav']['pageStatus'] = 'step2'
            else:
                context['messagebar'] = [{'type': 'error', 'content': 'No customer found'}]
        if action == 'createOrder':
            ctx = {}
            form = OrderForm(request.POST)
            log.info('create order %s' % form)
            if form.is_valid():
                userLoginId = request.session['up']['userloginid']
                # log.info('user id:%s' % userLoginId)
                u = UserLogin.objects.get(id=userLoginId)
                orderType = OrderType.objects.get(pk='SA01')
                customerid = request.session.get('existBP', None)
                log.info('customer id %s' % customerid)
                # bp = None
                if customerid:
                    bp = BP.objects.get(id=customerid)
                else:
                    # Save new BP
                    name1 = request.session['newCustomer']['name1']
                    district = request.session['newCustomer'].get('district', None)
                    if not district:
                        district = request.POST.get('district', None)
                    bp = BP()
                    bp.type = BPType.objects.get(pk='CO')
                    bp.name1 = name1
                    address = Address()
                    address.type = AddressType.objects.get(pk='ST')
                    address.district = DistrictType.objects.get(pk=district)
                    address.save()
                    bp.address1 = address
                    bp.save()

                    # Save relation
                    company = BP.objects.filter(type='ZZ')[0]
                    bpr = BPRelation()
                    bpr.bpA = company
                    bpr.bpB = bp
                    bpr.relation = BPRelType.objects.get(pk='C1')
                    bpr.save()

                # Save Order
                description = form.cleaned_data.get('description', '')
                stage = form.cleaned_data['stage']
                priority = form.cleaned_data['priority']
                status = form.cleaned_data['status']
                channel = form.cleaned_data['channel']
                empResp = form.cleaned_data['empResp']
                travelAmount = form.cleaned_data['travelAmount']
                amount = form.cleaned_data['amount']
                goLiveDate = form.cleaned_data['goLiveDate']
                text = form.cleaned_data['text']

                newOrder = Order()
                newOrder.description = description
                newOrder.createdBy = u.userbp
                newOrder.updatedBy = u.userbp
                newOrder.type = orderType
                pt = PriorityType.objects.filter(orderType=orderType, key=priority)[0]
                newOrder.priority = pt
                st = StatusType.objects.filter(orderType=orderType, key=status)[0]
                newOrder.status = st
                newOrder.save()

                # Save customer
                OrderPFNew_or_update(newOrder, '00001', bp)

                # Save Employee Responsible
                OrderPFNew_or_update(newOrder, '00003', BP.objects.get(id=empResp))

                # Save channel
                OrderPFNew_or_update(newOrder, '00002', BP.objects.get(id=channel))

                # Get OrderCustomized record
                orderCust = GetOrderCustNew_or_update(newOrder)
                # Save stage
                t = OrderExtSelectionFieldType.objects.get(id=stage)
                # OrderEFNew_or_update(newOrder,'00003',None,None,None,t)
                orderCust.stage = t.key

                # Save trave amount
                # OrderEFNew_or_update(newOrder,'00004',travelAmount,None,None,None)
                orderCust.travelAmount = travelAmount

                # Save amount
                # OrderEFNew_or_update(newOrder,'00005',amount,None,None,None)
                orderCust.amount = amount

                # Save go live date
                # OrderEFNew_or_update(newOrder,'00006',goLiveDate,None,None,None)
                orderCust.goLiveDate = goLiveDate
                orderCust.save()

                if text:
                    newText = OrderText()
                    newText.order = newOrder
                    newText.type = TextType.objects.get(pk='T001')
                    newText.content = text
                    newText.createdBy = u.userbp
                    newText.save()
                newOrder.save()
                log.info('BP saved')
                ctx['messagebar'] = [{'type': 'info', 'content': 'order saved'}]
                context.push(ctx)
                return self.view
            else:
                ctx['messagebar'] = [{'type': 'error', 'content': form.errors}]
                context.push(ctx)
                context['nav']['pageStatus'] = 'step2'
                return self.view
            context['nav']['pageStatus'] = 'step3'
        return self.view

    def leave(self, request, context):
        pass


class TMCApp:
    def __init__(self):
        self.view = 'crm/tmclist.html'

    def handle(self, request, context):
        action = request.POST.get('pageAction', '')
        params = request.POST.get('pageParams', None)
        if action == '':
            self.initialize(request, context)
        elif action == 'edit':
            log.info('params %s' % params)
            bp = BP.objects.get(id=params)
            # Get bp text
            texts = bp.bptext_set.all().order_by('-createdAt')
            context['nav']['pageStatus'] = 'edit'
            context['model'] = bp
            if texts:
                logText = ''
                for l in texts:
                    # Build log
                    t = '%s %s %s<br>----------<br>%s' % (
                        l.type.description, l.createdBy.displayName(),
                        timezone.localtime(l.createdAt).strftime('%Y-%m-%d %H:%M:%S'),
                        l.content)

                    logText = '%s%s<br><br>' % (logText, t)
                context['modelText'] = logText
            request.session['tmcId'] = bp.id
        elif action == 'save':
            touched = request.POST.get('touched', False)
            signed = request.POST.get('signed', False)
            connected = request.POST.get('connected', False)
            text = request.POST.get('text', False)
            address = request.POST.get('address', False)
            district = request.POST.get('district', False)
            log.info('%s %s %s' % (touched, signed, connected))
            tmcId = request.session.get('tmcId', None)
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
                bpcust.boolAttribute1 = bool(touched)
                bpcust.boolAttribute2 = bool(signed)
                bpcust.boolAttribute3 = bool(connected)
                bpcust.save()
                if text:
                    bpText = BPText()
                    bpText.bp = tmc
                    bpText.type = BPTextType.objects.get(pk='MEMO')
                    bpText.content = text
                    bpText.createdBy = getCurrentUserBp(request)
                    bpText.save()
                if address and district:
                    oldAddress = tmc.address1
                    if oldAddress is None:
                        newAddress = Address()
                        newAddress.type = AddressType.objects.get(pk='ST')
                        newAddress.address1 = address
                        newAddress.district = DistrictType.objects.get(pk=district)
                        newAddress.save()
                        tmc.address1 = newAddress
                        tmc.save()
                    else:
                        oldAddress.address1 = address
                        oldAddress.district = DistrictType.objects.get(pk=district)
                        oldAddress.save()
            self.initialize(request, context)
        elif action == 'cancel':
            self.initialize(request, context)
        return self.view

    def initialize(self, request, context):
        if request.session.get('tmcId', False):
            del request.session['tmcId']
        context['nav']['pageStatus'] = ''
        # com = getCurrentCompany()
        # tmcs = BP.objects.filter(asBPB__bpA=com, asBPB__relation='TM').all()
        # for tmc in tmcs:
        #     texts = tmc.bptext_set.all().order_by('-createdAt')
        #     if texts:
        #         tmc.latestText = texts[0].content
        #     else:
        #         tmc.latestText = ''
        # context['tmcs'] = tmcs

    def leave(self, request, context):
        pass


class HomeApp:
    def __init__(self):
        self.view = 'crm/home.html'
        self.name = 'home'

    def handle(self, request, context):
        log.info('process home')
        # Dashboard data
        # com = getCurrentCompany()
        # bprs = BPRelation.objects.all()

        # Employee number
        # empNum = bprs.filter(bpA=com,relation='A1').count()
        # context.push({'empNum':empNum})

        # Customer number
        # custNum = bprs.filter(bpA=com,relation='C1').count()
        # context.push({'custNum':custNum})

        # TMC number
        # tmcNum = bprs.filter(bpA=com,relation='TM').count()
        # context.push({'tmcNum':tmcNum})

        # Order stage
        # Oder data grouped by stage
        legend = []
        data = []
        countData = []
        traAmtCountData = []
        amtCountData = []
        highChartFunnelData = []
        # Get all stages
        stages = OrderExtSelectionFieldType.objects.filter(fieldKey='00003')
        # Get all order without the pending one (Status E0005)
        allOrders = Order.objects.filter(Q(deleteFlag=False), Q(type='SA01'), ~Q(status__key='E0005'))
        for stage in stages:
            orders = allOrders.filter(ordercustomized__stage=stage.key)
            (count, tamt, amt) = getOrderStatics(orders)
            name = stage.description
            legend.append(name)
            data.append({'name': name, 'value': count})
            countData.append(count)
            traAmtCountData.append(tamt)
            amtCountData.append(amt)
            highChartFunnelData.append([name, count])
        """
        [
                ['触达',   25],
                ['意向',       12],
                ['资质', 6],
                ['山航签约',    3],
                ['签约',    8],
                ['上线',21]
        ]
        """
        highChartFunnelSerialDataList = []
        highChartFunnelSerialData = {}
        highChartFunnelSerialData['name'] = getPhrase(request, 'g_default', 'count')
        highChartFunnelSerialData['data'] = highChartFunnelData
        highChartFunnelSerialDataList.append(highChartFunnelSerialData)
        highChartOption = getHighChartOptionTemplate()
        highChartOption['series'] = highChartFunnelSerialDataList
        context['highChartOption'] = json.dumps(highChartOption)
        opt = getEChartOptionTemplate()
        opt['tooltip']['formatter'] = "{b} : {c}"
        opt['series'][0]['type'] = 'bar'
        opt['series'][0]['data'] = countData
        opt['xAxis'] = [{'type': 'category', 'data': legend}]
        opt['yAxis'] = [{'type': 'value'}]
        context['stackOpt'] = json.dumps(opt)
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
        context['tastackOpt'] = json.dumps(opt)
        areaOpts = {}
        districts = DistrictType.objects.all()
        for area in districts:
            areaOrders = allOrders.filter(orderpf__pf='00001', orderpf__bp__address1__district=area.key)
            legend = []
            data = []
            countData = []
            traAmtCountData = []
            amtCountData = []
            highChartFunnelData = []
            for stage in stages:
                orders = areaOrders.filter(ordercustomized__stage=stage.key)
                if orders.count() == 0:
                    continue
                (count, tamt, amt) = getOrderStatics(orders)
                name = stage.description
                legend.append(name)
                data.append({'name': name, 'value': count})
                countData.append(count)
                traAmtCountData.append(tamt)
                amtCountData.append(amt)
                highChartFunnelData.append([name, count])
            highChartFunnelSerialDataList = []
            highChartFunnelSerialData = {}
            highChartFunnelSerialData['name'] = getPhrase(request, 'g_default', 'count')
            highChartFunnelSerialData['data'] = highChartFunnelData
            highChartFunnelSerialDataList.append(highChartFunnelSerialData)
            highChartOption = getHighChartOptionTemplate()
            highChartOption['series'] = highChartFunnelSerialDataList
            sopt = getEChartOptionTemplate()
            sopt['tooltip']['formatter'] = "{b} : {c}"
            ta = getPhrase(request, 'order', 'travelAmount')
            a = getPhrase(request, 'order', 'amount')
            sopt['legend']['data'] = [ta, a]
            sopt['series'][0]['name'] = ta
            sopt['series'][0]['type'] = 'bar'
            sopt['series'][0]['data'] = traAmtCountData
            sopt['series'].append({})
            sopt['series'][1]['name'] = a
            sopt['series'][1]['type'] = 'bar'
            sopt['series'][1]['data'] = amtCountData
            sopt['xAxis'] = [{'type': 'category', 'data': legend}]
            sopt['yAxis'] = [{'type': 'value'}]
            sopt['title']['text'] = area.description
            sopt['title']['x'] = 'center'
            areaOrders = WrapSaleLeadOrders(areaOrders)
            areaOpts[area.key] = {'pieOpt': json.dumps(highChartOption), 'stackOpt': json.dumps(sopt),
                                  'orders': areaOrders}
        context['areaOpts'] = areaOpts
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
                context['tmcData'] = json.dumps(tmcData)

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

                context['goLiveTmcTAmtPieOpt'] = json.dumps(opt)

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
                context['goLiveTmcTAmtPmtStackOpt'] = json.dumps(sopt)
        return self.view

    def leave(self, request, context):
        pass


class ChgLanApp:
    def __init__(self):
        self.view = 'crm/home.html'
        self.name = 'chlan'

    # self.isLogin=False
    def handle(self, request, context):
        lan = request.POST.get('pageParams', None)
        log.info('post get lan is %s', lan)
        if lan:
            request.session['lan'] = context['lan'] = lan
        return self.view

    def leave(self, request, context):
        pass


class CalendarServiceApp:
    """
    The class handle all json post request and return json data
    """

    def __init__(self):
        self.name = 'calendarsvr'

    def handle(self, request, context):
        try:
            return self.handleSvr(request, context)
        except Exception, e:
            response = {'code': -1, 'desc': e.message}
            return HttpResponse(json.dumps(response))

    def handleSvr(self, request, context):
        action = context['nav']['pageAction']
        response = {'code': -1, 'desc': 'unexpected error'}
        userBp = getCurrentUserBp(request)
        if action == 'getEvents':
            start = request.POST.get('start', None)
            end = request.POST.get('end', None)
            filter = {}
            filter['type'] = 'AC01'
            filter['deleteFlag'] = False
            if start:
                start = datetime.datetime.strptime(start, '%Y-%m-%d')
                filter['activity__startDateTime__gte'] = start
            if end:
                end = datetime.datetime.strptime(end, '%Y-%m-%d')
                filter['activity__endDateTime__lte'] = end
            orders = Order.objects.filter(**filter)
            events = []
            for o in orders:
                event = {}
                event['id'] = o.id
                event['title'] = '%s:%s' % (o.createdBy.displayName(), o.description)
                event['start'] = o.activity.startDateTime.strftime('%Y-%m-%d %H:%M')
                event['end'] = o.activity.endDateTime.strftime('%Y-%m-%d %H:%M')
                eventColor = None
                up = UserParameter.objects.filter(userlogin__userbp__id=o.createdBy.id, name='calender_event_color')
                if up:
                    eventColor = up[0].value
                if eventColor:
                    event['backgroundColor'] = eventColor
                else:
                    if o.createdBy.id == userBp.id:
                        event['backgroundColor'] = '#73a839'
                if o.createdBy.id != userBp.id:
                    event['editable'] = False
                events.append(event)
            response = events
        elif action == 'view':
            response = {}
            eventId = context['nav']['pageParams']
            order = Order.objects.get(id=eventId)
            event = {}
            event['id'] = order.id
            event['title'] = order.description
            event['startDate'] = order.activity.startDateTime.strftime('%Y-%m-%d %H:%M')
            event['endDate'] = order.activity.endDateTime.strftime('%Y-%m-%d %H:%M')
            # Set customer BP id
            orderPF = order.orderpf_set.filter(pf__key='00001')
            if orderPF:
                event['customer'] = [orderPF[0].bp.id, orderPF[0].bp.displayName()]
            else:
                event['customer'] = ['', '']
            texts = order.ordertext_set.filter(type='A001').order_by('-createdAt')
            if texts:
                event['text'] = texts[0].content
            if order.activity.visibility == 'PUB':
                event['visible'] = {'key': 'PUB', 'desc': '公开'}
            else:
                event['visible'] = {'key': 'PRT', 'desc': '私密'}
            response['editable'] = order.createdBy.id == userBp.id
            response['event'] = event
            response['code'] = 0
        elif action == 'save':
            eventId = context['nav']['pageParams']
            startDate = request.POST.get('startDate', None)
            endDate = request.POST.get('endDate', None)
            text = request.POST.get('text', None)
            visible = request.POST.get('visible', None)
            title = request.POST.get('title', None)
            customer = request.POST.get('customer', None)
            with transaction.atomic():
                if eventId:
                    order = Order.objects.get(id=eventId)
                else:
                    order = Order()
                    order.type = OrderType.objects.get(pk='AC01')
                    order.createdBy = userBp
                    # order.priority = PriorityType.objects.get(id=1)
                    # order.status = StatusType.objects.get(id=1)
                order.description = title
                order.updatedBy = userBp
                order.save()
                if not hasattr(order, 'activity'):
                    order.activity = Activity()
                startDate = startDate + ":00"
                d = datetime.datetime.strptime(startDate, '%Y-%m-%d %H:%M:%S')
                d = d.replace(tzinfo=pytz.timezone('UTC'))
                order.activity.startDateTime = d
                endDate = endDate + ":00"
                d = datetime.datetime.strptime(endDate, '%Y-%m-%d %H:%M:%S')
                d = d.replace(tzinfo=pytz.timezone('UTC'))
                order.activity.endDateTime = d
                order.activity.visibility = visible
                order.activity.save()
                customerBp = None
                try:
                    customerBp = BP.objects.get(id=customer)
                except Exception, e:
                    customerBp = None
                if customerBp:
                    OrderPFNew_or_update(order, '00001', customerBp)
                else:
                    OrderPFDelete(order, '00001', None)
                newText = OrderText()
                newText.order = order
                newText.type = TextType.objects.get(pk='A001')
                newText.content = text
                newText.createdBy = userBp
                newText.save()
                order.save()

                # Save this activity as a memo in sales order
                # There should be only one sales order related to this customer
                if customerBp:
                    saleOrder = Order.objects.filter(deleteFlag=False, type='SA01', orderpf__pf__key='00001',
                                                     orderpf__bp=customerBp)
                    if saleOrder:
                        saleOrder = saleOrder[0]
                        saleOrderText = """%s - %s %s
                        %s
                        """ % (startDate, endDate, title, text)
                        newText = OrderText()
                        newText.order = saleOrder
                        newText.type = TextType.objects.get(pk='T002')
                        newText.content = saleOrderText
                        newText.createdBy = userBp
                        newText.save()
            response = {'code': 0, 'desc': 'saved'}
        elif action == 'delete':
            eventId = context['nav']['pageParams']
            if eventId:
                order = Order.objects.get(id=eventId)
                if order.createdBy.id == userBp.id:
                    order.deleteFlag = True
                    order.save()
                    # order.delete()
            response = {'code': 0, 'desc': 'deleted'}
        elif action == 'saveColor':
            colorStr = request.POST.get('color', None)
            userLogin = getCurrentUser(request)
            up = UserParameter.objects.filter(userlogin=userLogin, name='calender_event_color')
            if up:
                up = up[0]
            else:
                up = UserParameter()
                up.userlogin = userLogin
                up.name = 'calender_event_color'
            up.value = colorStr
            up.save()
            response = {'code': 0, 'desc': 'saved'}
        elif action == 'getMyCust':
            result = []
            orders = Order.objects.filter(type='SA01', deleteFlag=False, orderpf__pf__key='00003', orderpf__bp=userBp)
            opf = OrderPF.objects.filter(order__in=orders, pf__key='00001')
            for pf in opf:
                result.append((pf.bp.id, pf.bp.displayName()))
            result.insert(0, ('', '&nbsp;'))
            response['code'] = 0
            response['desc'] = 'success'
            response['customers'] = result
        return HttpResponse(json.dumps(response))

    def leave(self, request, context):
        pass


class ServiceApp:
    """
    The class handles json post request and return json data
    """

    def __init__(self):
        self.name = 'service'

    def handle(self, request, context):
        action = context['nav']['pageAction']
        response = {'code': -1, 'desc': 'unexpected error'}
        userLogin = getCurrentUser(request)
        if action == 'savenickname':
            up = request.session.get('up', None)
            nickName = request.POST.get('nickName', None)
            if up:
                userLogin.user.nickName = nickName
                userLogin.user.save()
                userLogin.save()
                user = request.session.get('up', {})
                user['username'] = userLogin.user.nickName
                user['userloginid'] = userLogin.id
                request.session['up'] = user
                context.push({'up': user})
                response = {'code': 0, 'desc': 'saved'}
            else:
                log.info('userModel is None')
                response = {'code': 1, 'desc': 'error'}
        elif action == 'savepassword':
            oldPassword = request.POST.get('oldPassword', None)
            oldPasswordEncrypted = hashlib.sha1(oldPassword).hexdigest()
            newPassword = request.POST.get('newPassword', None)
            newPassword2 = request.POST.get('newPassword2', None)
            if userLogin.password != oldPasswordEncrypted:
                response['code'] = 1
                response['desc'] = 'Wrong old password'
                return HttpResponse(json.dumps(response))
            if newPassword != newPassword2:
                response['code'] = 2
                response['desc'] = 'New password not match'
                return HttpResponse(json.dumps(response))
            # Find to save new password
            userLogin.password = hashlib.sha1(newPassword).hexdigest()
            if not userLogin.passwordEncrypted:
                userLogin.passwordEncrypted = True
            userLogin.save()
            response['code'] = 0
            response['desc'] = 'saved'
        return HttpResponse(json.dumps(response))

    def leave(self, request, context):
        pass


# Order Service App
class OrderServiceApp:
    """
    The class handles json post request and return json data
    """

    def __init__(self):
        self.name = 'ordersvr'

    def handle(self, request, context):
        action = context['nav']['pageAction']
        response = {'code': -1, 'desc': 'unexpected error'}
        userLogin = getCurrentUser(request)
        if action == 'view':
            orderId = context['nav']['pageParams']
            try:
                order = Order.objects.get(id=orderId)

                orderBe = getBusinessEntity(order.type.key, order, request)
                # order = WrapSaleLeadOrder(order)
                orderJson = {}
                _, orderJson['title'] = GetFieldValueByFieldKey(orderBe, 'description')
                _, orderJson['customer'] = GetFieldValueByFieldKey(orderBe, 'customer')
                _, orderJson['stage'] = GetFieldValueByFieldKey(orderBe, 'stage')
                _, orderJson['channel'] = GetFieldValueByFieldKey(orderBe, 'channel')
                _, orderJson['empResp'] = GetFieldValueByFieldKey(orderBe, 'empResp')
                _, orderJson['priority'] = GetFieldValueByFieldKey(orderBe, 'priority')
                _, orderJson['status'] = GetFieldValueByFieldKey(orderBe, 'status')
                _, orderJson['travelAmount'] = GetFieldValueByFieldKey(orderBe, 'travelAmount')
                _, orderJson['amount'] = GetFieldValueByFieldKey(orderBe, 'amount')
                _, orderJson['customerType'] = GetFieldValueByFieldKey(orderBe, 'customerType')
                _, orderJson['settleType'] = GetFieldValueByFieldKey(orderBe, 'settleType')
                _, orderJson['goLiveDate'] = GetFieldValueByFieldKey(orderBe, 'goLiveDate')
                _, orderJson['text'] = GetFieldValueByFieldKey(orderBe, 'text')
                response['code'] = 0
                response['desc'] = 'success'
                response['order'] = orderJson
            except Exception, e:
                response = {'code': 1, 'desc': 'wrong order id'}
        elif action == "list":
            params = context['nav']['pageParams'].split(',')
            bpId = params[0]
            statusKey = params[1]
            result = []
            saleOrders = Order.objects.filter(type='SA01', deleteFlag=False, orderpf__pf='00003', orderpf__bp__id=bpId,
                                              status__key=statusKey)
            for order in saleOrders:
                orderBe = getBusinessEntity(order.type.key, order, request)
                # order = WrapSaleLeadOrder(order)
                orderJson = {}
                _, orderJson['title'] = GetFieldValueByFieldKey(orderBe, 'description')
                # _, orderJson['customer'] = GetFieldValueByFieldKey(orderBe, 'customer')
                _, orderJson['stage'] = GetFieldValueByFieldKey(orderBe, 'stage')
                _, orderJson['channel'] = GetFieldValueByFieldKey(orderBe, 'channel')
                # _, orderJson['empResp'] = GetFieldValueByFieldKey(orderBe, 'empResp')
                # _, orderJson['priority'] = GetFieldValueByFieldKey(orderBe, 'priority')
                # _, orderJson['status'] = GetFieldValueByFieldKey(orderBe, 'status')
                _, orderJson['travelAmount'] = GetFieldValueByFieldKey(orderBe, 'travelAmount')
                _, orderJson['amount'] = GetFieldValueByFieldKey(orderBe, 'amount')
                _, orderJson['customerType'] = GetFieldValueByFieldKey(orderBe, 'customerType')
                _, orderJson['settleType'] = GetFieldValueByFieldKey(orderBe, 'settleType')
                _, orderJson['goLiveDate'] = GetFieldValueByFieldKey(orderBe, 'goLiveDate')
                # _, orderJson['text'] = GetFieldValueByFieldKey(orderBe, 'text')
                # _, orderJson['latestText'] = GetFieldValueByFieldKey(orderBe, 'latestText')
                result.append(orderJson)
            response['code'] = 0
            response['desc'] = 'success'
            response['result'] = result
        resStr = json.dumps(response)
        print "Return : %s" % resStr
        return HttpResponse(resStr)

    def leave(self, request, context):
        pass


# Report Service App
class ReportServiceApp:
    """
    The class handles json post request and return json data
    """

    def __init__(self):
        self.name = 'reportsvr'

    def handle(self, request, context):
        action = context['nav']['pageAction']
        response = {'code': -1, 'desc': 'unexpected error'}
        userLogin = getCurrentUser(request)
        if action == 'salesmanRpt':
            # Get sales statistics by single salesman
            params = context['nav']['pageParams']
            saleOrders = Order.objects.filter(type='SA01', deleteFlag=False, orderpf__pf='00003',
                                              orderpf__bp__id=params)
            # build json result

            result = []
            statusSegDict = {}
            for order in saleOrders:
                statusSeg = statusSegDict.get(order.status.key, None)
                if not statusSeg:
                    statusSeg = {}
                    statusSeg['count'] = 0
                    statusSegDict[order.status.key] = statusSeg
                statusSeg['status'] = {}
                statusSeg['status']['title'] = order.status.description
                statusSeg['status']['key'] = order.status.key
                statusSeg['count'] = statusSeg['count'] + 1

                pass
        elif action == 'salesmanStatus':
            params = context['nav']['pageParams']
            saleOrders = Order.objects.filter(type='SA01', deleteFlag=False, orderpf__pf='00003',
                                              orderpf__bp__id=params)
            result = {}
            # r =  saleOrders.values("status__description","status").annotate(Count("status"))
            # for
            for s in StatusType.objects.filter(orderType='SA01').order_by('sortOrder'):
                count = saleOrders.filter(status=s).count()
                if count != 0:
                    result[s.description] = count
            response['code'] = 0
            response['desc'] = 'success'
            response['result'] = result
        return HttpResponse(json.dumps(response))

    def leave(self, request, context):
        pass


# Report Service App
class AttachmentApp:
    """
    The class handles json post request and return json data
    """

    def __init__(self):
        self.name = 'attachment'
        self.view = 'crm/attachment.html'

    def handle(self, request, context):
        action = context['nav']['pageAction']
        params = context['nav']['pageParams']
        if action == "":
            fa = FileAttachment.objects.filter(deleteFlag=False)
            files = []
            for f in fa:
                file = {}
                file['id'] = f.id
                file['name'] = f.file._get_path().split('/')[-1]
                file['description'] = f.description
                file['version'] = f.version
                files.append(file)
            context['files'] = files
            return self.view
        elif action == "download":
            fileId = context['nav']['pageParams']
            fa = FileAttachment.objects.get(id=fileId)
            # filename = fa.file._get_path().split('/')[-1]
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
        elif action == 'delete':
            authParams = {'name': 'auth', 'value': 'DocumentAccess', 'value2': '1'}
            if checkAuthObject(context, **authParams):
                fileId = context['nav']['pageParams']
                if fileId:
                    fa = FileAttachment.objects.get(id=fileId)
                    fa.deleteFlag = True
                    fa.save()
            return HttpResponse('')
        elif action == "uploadFile":
            # On standard view layout (Order, BP) uploading a file
            if request.FILES and request.FILES.get('file'):
                upfile = request.FILES.get('file')
                uploadFilesTemp = UploadFilesTemp()
                uploadFilesTemp.normalFile = upfile
                uploadFilesTemp.save()
                result = {'tempfileid': uploadFilesTemp.id}
                return HttpResponse(json.dumps(result))
            else:
                return HttpResponse(json.dumps(''))
        elif action == 'downloadFile':
            # On standard view layout (Order, BP) downloading a file
            # Get filename and path from user session, stored by logic in UtilTag, field type "FI"
            fieldKey = context['nav']['pageParams']
            fa = request.session.get('%s_file' % fieldKey, None)
            if fa:
                filename = fa['filename']
                filepath = fa['filepath']
                data = open(filepath).read()
                clientSystem = request.META['HTTP_USER_AGENT']
                if clientSystem.find('Windows') > -1:
                    filename = filename.encode('cp936')
                else:
                    filename = filename.encode('utf-8')
                response = HttpResponse(data, content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response
            else:
                return HttpResponse("")
        elif action == "uploadImg":
            # On standard view layout (Order, BP) uploading a image file
            if request.FILES and request.FILES.get('file'):
                upfile = request.FILES.get('file')
                uploadFilesTemp = UploadFilesTemp()
                uploadFilesTemp.imageFile = upfile
                uploadFilesTemp.save()
                result = {'tempfileid': uploadFilesTemp.id}
                return HttpResponse(json.dumps(result))
            else:
                return HttpResponse('')
        elif action == 'downloadImg':
            # On standard view layout (Order, BP) downloading a image file
            # Get filename and path from user session, stored by logic in UtilTag, field type "IF"
            fileId = context['nav']['pageParams']
            fa = UploadFilesTemp.objects.get(id=fileId)
            if fa.imageFile:
                result = base64.encodestring(fa.imageFile._get_file().read())
            else:
                result = ''
            return HttpResponse(result)
        elif action == "upload":
            if params == "corpLiscense":
                if request.FILES and request.FILES.get('file'):
                    upfile = request.FILES.get('file')
                else:
                    upfile = None
                # upfile = request.POST.get('file', None)
                bpId = request.POST.get('bpId', None)
                customer = BP.objects.get(id=bpId)
                if hasattr(customer, 'bpcustomized') and upfile:
                    customer.bpcustomized.corpLiscense = upfile
                    customer.bpcustomized.save()
                else:
                    bpcust = BPCustomized()
                    bpcust.corpLiscense = upfile
                    bpcust.bp = customer
                    bpcust.save()
                customer.save()
                return HttpResponse('')
            else:
                fuf = FileUploadForm(request.POST, request.FILES)
                print fuf
                if fuf.is_valid():
                    upfile = fuf.cleaned_data['file']
                    desc = fuf.cleaned_data['description']
                    version = fuf.cleaned_data['version']
                    fa = FileAttachment()
                    fa.file = upfile
                    fa.description = desc
                    fa.version = version
                    fa.actualfilename = upfile.name
                    fa.name = upfile.name
                    userBp = getCurrentUserBp(request)
                    fa.createdBy = userBp
                    fa.save()
                return self.view

    def leave(self, request, context):
        pass


# Sale Statistics App
class SaleStatisticApp:
    def __init__(self):
        self.name = 'salesstatistic'
        self.view = 'crm/sales_statistic.html'

    def handle(self, request, context):
        result = GetSalesStageData()
        context['result'] = result
        return self.view

    def leave(self, request, context):
        pass


# Model Service App
class ModelServiceApp:
    """
    This service work as a RESTful adapter to return model entitys
    """

    def __init__(self):
        self.name = 'modelsrv'
        self.view = ''

    def handle(self, request, context):
        # pageAction should be one of following
        # list - Return dictionary list of objects. E.g. [{'field':'value'},{..}]
        # get - Return single object. E.g {'field':'value'}
        # update - Update object
        # create - Create object
        # delete - Delete object
        #
        # pageParams should be the model class name
        action = request.POST.get('pageAction', '')
        params = request.POST.get('pageParams', None)

        modelSrv = modelApps.get(params, None)
        if modelSrv is None:
            return HttpResponse('')

        result = None
        kwargs = {'request': request}
        try:
            if action == 'create':
                result = modelSrv.create(None, **kwargs)
            elif action == 'get':
                result = modelSrv.get(None, **kwargs)
            elif action == 'update':
                result = modelSrv.update(None, **kwargs)
            elif action == 'getlist':
                result = modelSrv.getlist(None, **kwargs)
            result = json.dumps(result)
            return HttpResponse(result)
        except Exception, e:
            return HttpResponseBadRequest('')

    def leave(self, request, context):
        pass


# Create applications
bpApp = App()
bpApp.name = "bp"
bpApp.view = BPAppView('crm/bp.html')

commonOrderApp = App()
commonOrderApp.name = "commonOrder"
commonOrderApp.view = CommonOrderAppView('crm/commonOrder.html')

commonBpApp = App()
commonBpApp.name = "commonBp"
commonBpApp.view = CommonBpAppView('crm/commonBp.html')

newleadApp = CreateLeadApp()
newleadApp.name = "newlead"
tmcApp = TMCApp()
tmcApp.name = "tmc"
homeApp = HomeApp()
chlanApp = ChgLanApp()
calendarApp = CalendarApp()
calendarApp.name = "calendar"
calendarServiceApp = CalendarServiceApp()
serviceApp = ServiceApp()
orderServiceApp = OrderServiceApp()
reportServiceApp = ReportServiceApp()
attachmentApp = AttachmentApp()
salestatisticApp = SaleStatisticApp()

testFlowApp = StepBasedApp()
testFlowApp.name = 'stepapp'
testFlowApp.view = StepView('crm/test.html')

modelServiceApp = ModelServiceApp()

# Store application in dictionary globally
apps = {
    bpApp.name: bpApp,
    newleadApp.name: newleadApp,
    tmcApp.name: tmcApp,
    homeApp.name: homeApp,
    chlanApp.name: chlanApp,
    commonOrderApp.name: commonOrderApp,
    commonBpApp.name: commonBpApp,
    calendarApp.name: calendarApp,
    calendarServiceApp.name: calendarServiceApp,
    serviceApp.name: serviceApp,
    orderServiceApp.name: orderServiceApp,
    reportServiceApp.name: reportServiceApp,
    attachmentApp.name: attachmentApp,
    salestatisticApp.name: salestatisticApp,
    # testFlowApp.name: testFlowApp
    modelServiceApp.name: modelServiceApp
}

# Model Service class,
tmcModelService = TMCModelService()
customerModelService = CustomerModelService()
feedbackModelService = FeedbackModelService()
messageModelService = MessageModelService()
modelApps = {
    'tmc': tmcModelService,
    'customer': customerModelService,
    'feedback': feedbackModelService,
    'message': messageModelService
}


# Login form
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


# Handling login request
def login(request):
    if request.method == 'POST':
        uf = UserLoginForm(request.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            # Verify user
            (up, error) = verifyUser(username, password)
            # If system is in maintanence, show error
            isMaint, allowedUser = isSystemInMaintain()
            if isMaint == 'Y' and username not in allowedUser.split(';'):
                error = 'inMaint'
            if error:
                # Has error, display error message
                template = loader.get_template('crm/login.html')
                errorDesc = getPhrase(request, 'g_default', 'err.' + error)
                context = RequestContext(request, {
                    'errorDesc': errorDesc
                })
                return HttpResponse(template.render(context))
            if up:
                # User is valid, check user role
                request.session['up'] = up
                navLoc = ['home']
                request.session['navLoc'] = navLoc
                userAuth = up.get('userAuth', None)
                if not userAuth:
                    # No role authorization or profile assigned to user
                    up['loginRole'] = ''
                    error = 'noRole'
                    template = loader.get_template('crm/login.html')
                    errorDesc = getPhrase(request, 'g_default', 'err.' + error)
                    context = RequestContext(request, {
                        'errorDesc': errorDesc
                    })
                    return HttpResponse(template.render(context))
                roles = UserRoleType.objects.filter(key__in=up['userAuth']['roles'])
                log.info('roles:%s' % roles)
                up['loginRole'] = ''
                if roles.count() > 1:
                    # Multiple role assigned, show role selection screen
                    template = loader.get_template('crm/roleSelect.html')
                    context = RequestContext(request, {
                        'roles': roles
                    })
                    return HttpResponse(template.render(context))
                elif roles.count() == 1:
                    # Only 1 role assigned, show home page
                    up['loginRole'] = roles[0].key
                    up['loginRoleName'] = roles[0].description
                    return HttpResponseRedirect('home')
                else:
                    # No role assigned to user
                    error = 'noRole'
                    template = loader.get_template('crm/login.html')
                    errorDesc = getPhrase(request, 'g_default', 'err.' + error)
                    context = RequestContext(request, {
                        'errorDesc': errorDesc
                    })
                    return HttpResponse(template.render(context))
            else:
                return HttpResponseRedirect('index')
        else:
            log.error('form invalid')
    else:
        uf = UserLoginForm()
    template = loader.get_template('crm/login.html')
    context = RequestContext(request, {
        'uf': uf
    })
    return HttpResponse(template.render(context))


# Handling logout
def logout(request):
    # Removing user session
    for k, v in request.session.items():
        del request.session[k]
    return HttpResponseRedirect('index')


# Home page, all request goes here
# @cache_page(60 * 15)
def home(request):
    startTime = time.time()
    ctx = {}
    nav = {}
    result = 'crm/home.html'
    # Create RequestCotext object
    context = RequestContext(request, ctx)
    isMaint, allowedUser = isSystemInMaintain()
    errorDesc = ''
    if isMaint == 'Y':
        errorDesc = getPhrase(request, 'g_default', 'err.inMaint')
    context['errorDesc'] = errorDesc
    if request.method == 'POST':
        # Get posted data : pageAction, pageParams, pageMode
        nav['pageApp'] = request.POST.get('pageApp', '')
        nav['pageAction'] = request.POST.get('pageAction', '')
        nav['pageParams'] = request.POST.get('pageParams', '')
        nav['pageMode'] = request.POST.get('pageMode', '')
    else:
        nav['pageApp'] = 'home'
    context['nav'] = nav
    navPath = request.session.get('navPath', [])
    navPath.append(nav)
    if len(navPath) > 10:
        del navPath[:5]
    request.session['nav'] = nav
    request.session['navPath'] = navPath
    chlanFlag = False
    # For app chlan, role selection
    if request.method == 'POST':
        pageApp = request.POST.get('pageApp', None)
        log.info('pageApp is %s' % pageApp)
        if pageApp == 'chlan':
            app = apps.get('chlan', None)
            if app:
                log.info('chan app')
                result = app.handle(request, context)
                if not checkIsUserLogin(request):
                    return THR(request, 'crm/login.html', context)
                else:
                    homeApp = apps['home']
                    result = homeApp.handle(request, context)
                    chlanFlag = True
        if pageApp == 'roleSelect':
            roleKey = request.POST.get('pageParams', None)
            # log.info('role key is %s' % roleKey)
            if roleKey:
                request.session['up']['loginRole'] = roleKey
    # User has login with proper role
    # initial context
    # Put language into context
    lan = request.session.get('lan', 'cn')
    request.session['lan'] = context['lan'] = lan
    # Check is user login, otherwise goes to login page
    if not checkIsUserLogin(request):
        return THR(request, 'crm/login.html', context)
    # Check is user role selected, otherwise goes to login page
    if not checkUserRole(request):
        return THR(request, 'crm/login.html', {'errorDesc': errorDesc})
    navLoc = request.session.get('navLoc', None)
    # Get user profile from session, this was set by in login method
    up = request.session.get('up', None)
    # Put up in context
    context.push({'up': up})

    userLogin = getCurrentUser(request)
    up = UserParameter.objects.filter(userlogin=userLogin, name='calender_event_color')
    if up:
        up = up[0]
        context['eventColor'] = up.value

    if chlanFlag:
        nav['pageApp'] = 'home'
    else:
        result = dispatch_pageApp(request, context, nav)
        logAppAccess(userLogin, nav)
    endTime = time.time()
    log.info('Dispatch app took %s' % (endTime - startTime))
    return forwardTo(request, context, result)


def forwardTo(request, context, result):
    """ Base on result type, return different view"""
    if isinstance(result, HttpResponse):
        # Got HttpResponse, return directly
        # This is for downloading xls file
        return result
    elif type(result) == dict:
        # A nav dictionary returned
        # The app class return a nav(pageApp,pageAction,pageParams,pageMode) dictionary, re-trigger the app
        # This is for back button to return to previous page
        # navPath=request.session.get('navPath',[])
        # navPath.pop()
        context['nav'] = result
        res = dispatch_pageApp(request, context, result)
        # Check result type again, incase back action in chain
        return forwardTo(request, context, res)
    else:
        # A nomral templage file name is returned
        startTime = time.time()
        thr = THR(request, result, context)
        endTime = time.time()
        log.info('Render response took %s', endTime - startTime)
        return thr


# User Profile Form
class UserProfileForm(forms.Form):
    nickName = forms.CharField()


# User Password Change Form
class UserChangePwdForm(forms.Form):
    oldPassword = forms.CharField()
    newPassword = forms.CharField()
    newPasswordAgain = forms.CharField()


# Dispatch page actions
def dispatch_pageApp(request, context, nav):
    pageApp = nav['pageApp']
    log.info('calling app [%s]' % pageApp)
    lastApp = request.session.get('lastApp', None)
    if lastApp and lastApp != pageApp:
        lApp = apps.get(lastApp, None)
        if lApp:
            print 'leave app %s' % lastApp
            lApp.leave(request, context)
    request.session['lastApp'] = pageApp
    app = apps.get(pageApp, None)
    page = ''
    if app:
        page = app.handle(request, context)
    else:
        try:
            log.info('calling app [%s]' % pageApp)
            return eval(pageApp)(request, context)
        except Exception, e:
            log.info('error in %s with %s' % (pageApp, e))
            page = 'crm/%s.html' % pageApp
    if isinstance(page, HttpResponse):
        log.info('HttpResponse returned')
    else:
        log.info('return page: %s' % page)
    return page


# Update nickname
def chgname(request, context):
    upf = UserProfileForm(request.POST)
    if upf.is_valid():
        log.info('UserProfileForm is valid')
        nickName = upf.cleaned_data['nickName']
        up = request.session.get('up', None)
        if up:
            userLogin = getCurrentUser(request)
            userLogin.user.nickName = nickName
            log.info('new nickname %s' % userLogin.user.nickName)
            userLogin.user.save()
            userLogin.save()
            user = request.session.get('up', {})
            user['username'] = userLogin.user.nickName
            user['userloginid'] = userLogin.id
            request.session['up'] = user
            context.push({'up': user})
        else:
            log.info('userModel is None')
    else:
        log.info('UserProfileForm is invalid')
        pass
    return 'crm/profile.html'


def roleSelect(request, context):
    roleKey = request.POST.get('pageParams', None)
    if roleKey:
        role = UserRoleType.objects.get(pk=roleKey)
        request.session['up']['loginRole'] = roleKey
        request.session['up']['loginRoleName'] = role.description
        context.push({'up': request.session['up']})
    return 'crm/home.html'


def orderSave(request):
    orderForm = OrderForm(request.POST)
    ctx = {}
    ctx['form'] = orderForm
    # log.info('orderForm:%s' % orderForm)
    if orderForm.is_valid():
        log.info('orderForm valid')
    else:
        log.info('orderForm invalid')
        return ('crm/newOrder.html', ctx)
    return ('crm/salesDetail.html', ctx)


def profile(request, context):
    userLogin = getCurrentUser(request)
    up = UserParameter.objects.filter(userlogin=userLogin, name='calender_event_color')
    if up:
        up = up[0]
        context['eventColor'] = up.value
    return 'crm/profile.html'


# Test page form
class TestPageForm(forms.Form):
    textfield1 = forms.CharField(required=True)


def testPage_2(request, context):
    return 'crm/testPage2.html'


def testPage_3(request, context):
    return 'crm/testPage3.html'


def testPage(request, context):
    log.info('testPage called with %s %s' % (request, context))

    # context['username']=username

    fieldsStr = request.POST.get('fields', None)
    print fieldsStr
    for f in fieldsStr.split(','):
        value = request.POST.get(f, None)
        print value

    # value = request.POST.get('a0', None)
    # print value
    # value = request.POST.get('a1', None)
    # print value
    return 'crm/testPage.html'


def view(request, context):
    type = request.POST.get('pageParams', None)
    if type:
        return standCRUDProcess(request, context, type)
    else:
        return 'crm/error.html'


def standCRUDProcess(request, context, type):
    log.info('%s' % context['nav'])
    nav = context['nav']

    status = request.session.get('pageStatus', '')
    if nav['pageMode'] == '':
        log.info('Entry point')
        status = 'search'
    elif status == 'search' and nav['pageMode'] == 'search':
        log.info('do search')
        status = 'result'
    elif status == 'result' and nav['pageMode'] == 'view':
        log.info('show detail')
        status = 'detail'
    elif status == 'detail' and nav['pageMode'] == 'edit':
        log.info('go into edit mode')
        status = 'edit'
    elif status == 'detail' and nav['pageMode'] == 'back':
        log.info('goback')
        status = 'result'
    elif status == 'edit':
        if nav['pageMode'] == 'save':
            log.info('save data')
        if nav['pageMode'] == 'cancel':
            log.info('cancel save')
        status = 'detail'
    request.session['pageStatus'] = status
    nav['pageStatus'] = status
    page = 'crm/%s.html' % type
    return page


def viewCustomer(request, context):
    bpId = request.POST.get('pageParams', None)
    if bpId:
        model = BP.objects.get(id=bpId)
        context.push({'model': model})
    return 'crm/customerDetail.html'


class CustomerForm(forms.Form):
    name1 = forms.CharField(max_length=255, required=True)


def myOrder(request, context):
    ctx = {}
    stages = OrderExtSelectionFieldType.objects.filter(orderType='SA01', fieldKey='00003')
    statuses = StatusType.objects.filter(orderType='SA01')
    # Check authorization and render data
    p = {}
    p['name'] = 'profile'
    p['value'] = 'P_SALE_LEADER'
    authPass = checkAuthObject(context, **p)
    if authPass:
        # Data for P_SALE_LEADER
        # Org chart
        #               Department -- Employee
        #                    |
        #        |-----------|------------|
        #       D1--E        D2--E        D3--E
        #    |--|--|     |---|---|   |----|----|
        #   E1 E2  E3    E4  E5  E6 E7   E8    E9
        #
        myBP = getCurrentUserBp(request)
        # Get my current org (as a leader)
        salesmen = None
        myOrg = [bpr.bpA for bpr in BPRelation.objects.filter(bpB__exact=myBP, relation='MA', bpA__type='OR')]
        if myOrg:
            myOrg = myOrg[0]
            salesmen = GetAllEmployeeUnderOrg(myOrg)
        # salesmen = [bpr.bpB for bpr in BPRelation.objects.filter(bpA__in=myOrg, relation="BL")]
        if not salesmen:
            salesmen = BP.objects.filter(
                Q(valid=True),
                Q(asBPB__relation__key='BL'),
                Q(asBPB__bpA__partnerNo=1) | Q(asBPB__bpA__partnerNo=2) | Q(asBPB__bpA__partnerNo=3)).all()
        list = []
        saleOrderIds = []
        for salesman in salesmen:
            saleOrders = Order.objects.filter(type='SA01', deleteFlag=False, orderpf__pf='00003', orderpf__bp=salesman)
            saleOrderIds.extend([o.id for o in saleOrders])
            if saleOrders.count() == 0:
                continue
            legend = []
            data = []
            countData = []
            traAmtCountData = []
            amtCountData = []
            highChartFunnelData = []
            for stage in stages:
                orders = saleOrders.filter(ordercustomized__stage=stage.key)
                if orders.count() == 0:
                    continue
                (count, tamt, amt) = getOrderStatics(orders)
                name = stage.description
                legend.append(name)
                data.append({'name': name, 'value': count})
                countData.append(count)
                traAmtCountData.append(tamt)
                amtCountData.append(amt)
                highChartFunnelData.append([name, count])
            highChartFunnelSerialDataList = []
            highChartFunnelSerialData = {}
            highChartFunnelSerialData['name'] = getPhrase(request, 'g_default', 'count')
            highChartFunnelSerialData['data'] = highChartFunnelData
            highChartFunnelSerialDataList.append(highChartFunnelSerialData)
            highChartOption = getHighChartOptionTemplate()
            highChartOption['series'] = highChartFunnelSerialDataList
            sopt = getEChartOptionTemplate()
            sopt['tooltip']['formatter'] = "{b} : {c}"
            ta = getPhrase(request, 'order', 'travelAmount')
            a = getPhrase(request, 'order', 'amount')
            sopt['legend']['data'] = [ta, a]
            sopt['series'][0]['name'] = ta
            sopt['series'][0]['type'] = 'bar'
            sopt['series'][0]['data'] = traAmtCountData
            sopt['series'].append({})
            sopt['series'][1]['name'] = a
            sopt['series'][1]['type'] = 'bar'
            sopt['series'][1]['data'] = amtCountData
            sopt['xAxis'] = [{'type': 'category', 'data': legend}]
            sopt['yAxis'] = [{'type': 'value'}]
            sopt['title']['x'] = 'center'
            orders = Order.objects.filter(deleteFlag=False, type='SA01', orderpf__pf='00003',
                                          orderpf__bp=salesman).order_by('-ordercustomized__stage')
            orders = WrapSaleLeadOrders(orders)
            list.append({'name': salesman.displayName,
                         'bpId': salesman.id,
                         'pieOpt': json.dumps(highChartOption),
                         'stackOpt': json.dumps(sopt),
                         'orders': orders
                         # 'status_E0001_count': status_E0001_count,
                         # 'status_E0004_count': status_E0004_count,
                         # 'status_E0005_count': status_E0005_count
                         })
            # 'dashboard':dashboard})
        ctx['list'] = list

        ctx['chglist'] = []

        start = datetime.datetime.now().date()
        end = start - datetime.timedelta(days=15)
        changeHistory = ChangeHistory. \
            objects.filter(Q(updatedAt__gte=end),
                           Q(type='Order'),
                           Q(objectId__in=saleOrderIds)) \
            .order_by("-updatedAt")
        changedOrderIds = ChangeHistory. \
            objects.filter(Q(updatedAt__gte=end),
                           Q(type='Order'),
                           Q(objectId__in=saleOrderIds)) \
            .values("objectId").distinct()
        chListAll = []
        stageList = {}
        statusList = {}
        orderStageChecked = {}
        orderStatusChecked = {}
        for oh in changeHistory:
            chList = {}
            updatedBy = BP.objects.get(id=oh.updatedBy).displayName()
            updatedAt = str(timezone.localtime(oh.updatedAt).strftime("%Y-%m-%d %H:%M:%S"))
            order = Order.objects.get(id=oh.objectId)
            if order.type.key != 'SA01':
                continue
            chList['orderId'] = oh.objectId
            orderDesc = order.description
            chList['orderDesc'] = orderDesc
            chList['orderField'] = getPhrase(request, 'order', oh.objectField)
            chList['newValue'] = oh.newValue
            chList['oldValue'] = oh.oldValue
            chList['updatedBy'] = updatedBy
            chList['updatedAt'] = updatedAt
            chListAll.append(chList)
            if oh.objectField == 'stage':
                checked = orderStageChecked.get(oh.objectId, None)
                if not checked:
                    l = stageList.get(oh.newValue, None)
                    if not l:
                        l = {}
                        l['title'] = oh.newValue
                        l['count'] = 0
                        l['records'] = []
                        stageList[oh.newValue] = l
                    # stageList[oh.newValue].append(order.id)
                    stageList[oh.newValue]['count'] = stageList[oh.newValue]['count'] + 1

                    stageList[oh.newValue]['records'].append({
                        'id': order.id,
                        'customer': OrderPFGetSingleBP(order, '00001').displayName(),
                        'empResp': OrderPFGetSingleBP(order, '00003').displayName()
                    })
                    orderStageChecked[oh.objectId] = True

            if oh.objectField == 'status':
                checked = orderStatusChecked.get(oh.objectId, None)
                if not checked:
                    l = statusList.get(oh.newValue, None)
                    if not l:
                        l = {}
                        l['title'] = oh.newValue
                        l['count'] = 0
                        l['records'] = []
                        statusList[oh.newValue] = l
                    # stageList[oh.newValue].append(order.id)
                    statusList[oh.newValue]['count'] = statusList[oh.newValue]['count'] + 1
                    statusList[oh.newValue]['records'].append({
                        'id': order.id,
                        'customer': OrderPFGetSingleBP(order, '00001').displayName(),
                        'empResp': OrderPFGetSingleBP(order, '00003').displayName()
                    })
                    orderStatusChecked[oh.objectId] = True
        ctx['chgListAll'] = chListAll
        ctx['stageList'] = stageList
        ctx['statusList'] = statusList

    u = getCurrentUser(request)
    orders = Order.objects.filter(deleteFlag=False, type='SA01', orderpf__pf='00003', orderpf__bp=u.userbp)
    # Oder data grouped by stage
    legend = []
    data = []
    countData = []
    highChartFunnelData = []
    for stage in stages:
        orderOfStage = orders.filter(type='SA01', ordercustomized__stage=stage.key)
        c = orderOfStage.count()
        if c == 0:
            continue
        legend.append(stage.description)
        (count, tamt, amt) = getOrderStatics(orderOfStage)
        name = "%s (%s个)" % (stage.description, count)
        data.append({'name': name, 'value': tamt})
        countData.append(c)
        highChartFunnelData.append([name, count])
    # opt = getEChartOptionTemplate()
    # opt['title']['text'] = ''
    # opt['series'][0]['name'] = 'name'
    # opt['series'][0]['data'] = data
    highChartFunnelSerialDataList = []
    highChartFunnelSerialData = {}
    highChartFunnelSerialData['name'] = getPhrase(request, 'g_default', 'count')
    highChartFunnelSerialData['data'] = highChartFunnelData
    highChartFunnelSerialDataList.append(highChartFunnelSerialData)
    highChartOption = getHighChartOptionTemplate()
    highChartOption['series'] = highChartFunnelSerialDataList

    # opt = getEChartOptionTemplate()
    # opt['title']['text'] = ''
    # opt['tooltip']['formatter'] = "{b}<br/>{c}万 {d}%"
    # # opt['legend']['data'] = legend
    # opt['series'][0]['name'] = 'name'
    # opt['series'][0]['data'] = data
    context['pieOpt'] = json.dumps(highChartOption)

    opt = getEChartOptionTemplate()
    opt['series'][0]['type'] = 'bar'
    opt['series'][0]['data'] = countData
    opt['xAxis'] = [{'type': 'category', 'data': legend}]
    opt['yAxis'] = [{'type': 'value'}]
    context['stackOpt'] = json.dumps(opt)
    orders = WrapSaleLeadOrders(orders)
    ctx['models'] = orders
    context.push(ctx)

    # Save result in session for xls output
    ms = []
    hds = []
    hd = {'col': 'desc', 'desc': getPhrase(request, 'order', 'shortName')}
    hds.append(hd)
    hd = {'col': 'empResp', 'desc': getPhrase(request, 'order', 'empResp')}
    hds.append(hd)
    hd = {'col': 'district', 'desc': getPhrase(request, 'order', 'district')}
    hds.append(hd)
    hd = {'col': 'travelAmount', 'desc': getPhrase(request, 'order', 'travelAmount')}
    hds.append(hd)
    hd = {'col': 'amount', 'desc': getPhrase(request, 'order', 'amount')}
    hds.append(hd)
    hd = {'col': 'goLiveDate', 'desc': getPhrase(request, 'order', 'goLiveDate')}
    hds.append(hd)
    hd = {'col': 'priority', 'desc': getPhrase(request, 'order', 'priority')}
    hds.append(hd)
    hd = {'col': 'status', 'desc': getPhrase(request, 'order', 'status')}
    hds.append(hd)
    hd = {'col': 'channel', 'desc': getPhrase(request, 'order', 'channel')}
    hds.append(hd)
    hd = {'col': 'stage', 'desc': getPhrase(request, 'order', 'stage')}
    hds.append(hd)
    hd = {'col': 'text', 'desc': getPhrase(request, 'order', 'text')}
    hds.append(hd)

    for model in orders:
        m = {}
        m['desc'] = model.description
        # log.info('%s' % type(model))
        m['empResp'] = model.empResp.displayName()
        if model.customer.address1:
            m['district'] = model.customer.address1.district.description
        else:
            m['district'] = ''
        m['travelAmount'] = model.ordercustomized.travelAmount
        m['amount'] = model.ordercustomized.amount
        m['goLiveDate'] = str(model.ordercustomized.goLiveDate)
        m['priority'] = model.priority.description
        m['status'] = model.status.description
        m['channel'] = model.channel.name1
        m['stage'] = model.ordercustomized.displayStage()
        m['text'] = model.latestText
        ms.append(m)
    xls = {}
    xls['hds'] = hds
    xls['ms'] = ms
    request.session['xlsoutput'] = xls

    return 'crm/myOrder.html'


def xlsoutput(request, context):
    xls = request.session.get('xlsoutput', None)
    if xls:
        ms = xls['ms']
        hds = xls['hds']
    else:
        ms = []
        hds = []
    return getXLS(request, ms, hds)


class OrderForm(forms.Form):
    description = forms.CharField(max_length=50)
    account = forms.CharField(max_length=50, required=True)
    empResp = forms.CharField()
    stage = forms.CharField()
    priority = forms.CharField()
    status = forms.CharField()
    channel = forms.CharField()
    travelAmount = forms.DecimalField(required=False)
    amount = forms.DecimalField(required=False)
    goLiveDate = forms.DateField(required=False, input_formats=['%Y-%m-%d'])
    text = forms.CharField(required=False)


def saveOrder(request, context):
    ctx = {}
    userLoginId = request.session['up']['userloginid']
    # log.info('user id:%s' % userLoginId)
    u = UserLogin.objects.get(id=userLoginId)
    orderType = OrderType.objects.get(pk='SA01')
    # bpTypeCO = BPType.objects.filter(key__exact='CO')[0]
    form = OrderForm(request.POST)
    ctx['form'] = form
    log.info('save order form is %s' % form)
    if form.is_valid():
        description = form.cleaned_data.get('description', '')
        bp = form.cleaned_data.get('account', '')
        stage = form.cleaned_data['stage']
        priority = form.cleaned_data['priority']
        status = form.cleaned_data['status']
        channel = form.cleaned_data['channel']
        travelAmount = form.cleaned_data['travelAmount']
        amount = form.cleaned_data['amount']
        goLiveDate = form.cleaned_data['goLiveDate']
        log.info('%s %s %s %s' % (description, stage, priority, status))
        newOrder = Order()
        newOrder.description = description
        newOrder.createdBy = u.userbp
        newOrder.updatedBy = u.userbp
        newOrder.type = orderType
        pt = PriorityType.objects.filter(orderType=orderType, key=priority)[0]
        newOrder.priority = pt
        st = StatusType.objects.filter(orderType=orderType, key=status)[0]
        newOrder.status = st
        newOrder.save()
        # Save customer
        OrderPFNew_or_update(newOrder, '00001', BP.objects.get(id=bp))
        # Save channel
        OrderPFNew_or_update(newOrder, '00002', BP.objects.get(id=channel))


        # Get OrderCustomized record
        orderCust = GetOrderCustNew_or_update(newOrder)
        # Save stage
        t = OrderExtSelectionFieldType.objects.get(id=stage)
        # OrderEFNew_or_update(newOrder,'00003',None,None,None,t)
        orderCust.stage = t.key

        # Save trave amount
        # OrderEFNew_or_update(newOrder,'00004',travelAmount,None,None,None)
        orderCust.travelAmount = travelAmount

        # Save amount
        # OrderEFNew_or_update(newOrder,'00005',amount,None,None,None)
        orderCust.amount = amount

        # Save go live date
        # OrderEFNew_or_update(newOrder,'00006',goLiveDate,None,None,None)
        orderCust.goLiveDate = goLiveDate
        orderCust.save()

        newOrder.save()
        log.info('BP saved')
        return myOrder(request, context)
    else:
        log.info('invalid order form')
        ctx['messagebar'] = [{'type': 'error', 'content': form.errors}]
        context.push(ctx)
        return myOrder(request, context)
    return 'crm/order.html'


def deleteOrder(request, context):
    orderId = request.POST.get('pageParams', None)
    # log.info('delete order id [%s]' % orderId)
    if orderId:
        # log.info('del order %s' % orderId)
        userbp = getCurrentUserBp(request)
        o = Order.objects.get(id=orderId)
        if o.createdBy.id == userbp.id:
            # Only who creates order can delete
            o.deleteFlag = True
            o.save()
        else:
            context['messagebar'] = [{'type': 'error', 'content': 'Not your order'}]
    return myOrder(request, context)


def chlan(request, context):
    lan = request.POST.get('pageParams', None)
    log.info('post get lan is %s', lan)
    ctx = {}
    if lan:
        request.session['lan'] = ctx['lan'] = lan
    context.push(ctx)
    return None


def allLeads(request, context):
    startTime = time.time()
    # Order stage
    # Oder data grouped by stage
    i = 1
    amount = 0
    charts = []
    charts.append({'pie': [], 'stack': []})
    charts.append({'pie': [], 'stack': []})
    charts.append({'pie': [], 'stack': []})
    models = Order.objects.filter(deleteFlag=False, type='SA01')
    models = WrapSaleLeadOrders(models)
    userbp = getCurrentUserBp(request)
    for model in models:
        model.createdByMe = model.createdBy.id == userbp.id

    endTime = time.time()
    log.info('AllLead step1 took %s', endTime - startTime)
    startTime = time.time()
    types = OrderExtSelectionFieldType.objects.filter(fieldKey='00003')
    for stage in types:
        c = OrderCustomized.objects.filter(order__type='SA01', stage=stage.key).aggregate(Sum('travelAmount'),
                                                                                          Count('order'))
        totalTravelAmount = c.get('travelAmount__sum', 0)
        c = OrderCustomized.objects.filter(order__type='SA01', stage=stage.key).aggregate(Sum('amount'), Count('order'))
        totalAmount = c.get('amount__sum', 0)
        totalOrder = c.get('order__count', 0)
        if totalTravelAmount == None:
            totalTravelAmount = 0
        if totalAmount == None:
            totalAmount = 0
        if totalOrder == None:
            totalOrder = 0
        data = []
        # Stage pie data
        v = totalOrder
        d = {'label': '%s - %d' % (stage.description, v), 'data': v}
        charts[0]['pie'].append(d)

        # Stage stack data
        d = {'label': '%s - %d' % (stage.description, v), 'data': [[i, v]]}
        charts[0]['stack'].append(d)

        # Travel amount stack
        d = {'label': '%s - %d' % (stage.description, totalTravelAmount), 'data': [[i, totalTravelAmount]]}
        charts[1]['stack'].append(d)
        # Amount stack
        d = {'label': '%s - %d' % (stage.description, totalAmount), 'data': [[i, totalAmount]]}
        charts[2]['stack'].append(d)
        i += 1
    for chart in charts:
        chart['pie'] = json.dumps(chart['pie'])
        chart['stack'] = json.dumps(chart['stack'])
    context['charts'] = charts
    context['models'] = models
    endTime = time.time()
    log.info('AllLead took %s', endTime - startTime)
    return 'crm/allLeads.html'


@csrf_exempt
def ajax(request):
    """
    This method handles ajax request
    For action require return code, return like {'code':0,desc:''}
    Others depends on needs
    """
    if not checkIsUserLogin(request):
        resp = json.dumps('')
        return HttpResponse(resp)

    if request.method == 'POST':
        type = request.POST.get('t', None)
        name = request.POST.get('n', None)
        value = request.POST.get('v', None)
        if type == 'up':
            userLogin = getCurrentUser(request)
            up = UserParameter.objects.filter(userlogin=userLogin, name=name)
            if up:
                up = up[0]
            else:
                up = UserParameter()
                up.userlogin = userLogin
                up.name = name
            up.value = value
            up.save()
            resp = json.dumps({'code': 0, 'desc': ''})
            return HttpResponse(resp)
        elif type == 'file':
            fuf = FileUploadForm(request.POST, request.FILES)
            print fuf
            if fuf.is_valid():
                upfile = fuf.cleaned_data['file']
                fp = open('media/upload/' + upfile.name, 'wb')
                fp.write(upfile.read())
                fp.close()
            resp = json.dumps({'code': 0, 'desc': ''})
            return HttpResponse(resp)
        resp = json.dumps({'code': 1, 'desc': 'Not supported'})
        return HttpResponse(resp)
    elif request.method == 'GET':
        result = []
        type = request.GET.get('t', None)
        if type == 'weekreport':
            interval = request.GET.get('i')
            option = request.GET.get('o')
            if not interval or not option:
                resp = json.dumps(result)
                return HttpResponse(resp)
            result = GetWeeklyReport(interval, option, request)
        elif type == 'myorders':
            bpId = request.GET.get('empResp', None)
            elasticAvailable = False
            if bpId is None:
                u = getCurrentUser(request)
                userBp = u.userbp
            else:
                userBp = BP.objects.get(id=bpId)
            orders = Order.objects.filter(deleteFlag=False, type='SA01', orderpf__pf='00003', orderpf__bp=userBp)
            orders = WrapSaleLeadOrders(orders)
            for order in orders:
                record = {}
                record['shortName'] = order.description
                if order.channel:
                    record['channel'] = order.channel.name1
                else:
                    record['channel'] = ''
                if order.ordercustomized:
                    record['stage'] = order.ordercustomized.displayStage()
                    record['travelAmount'] = order.ordercustomized.travelAmount
                    if order.ordercustomized.goLiveDate:
                        record['goLiveDate'] = order.ordercustomized.goLiveDate.strftime('%Y-%m-%d')
                    else:
                        record['goLiveDate'] = ''
                else:
                    record['stage'] = ''
                    record['travelAmount'] = ''
                    record['goLiveDate'] = ''
                if order.status:
                    record['status'] = order.status.description
                else:
                    record['status'] = ''
                record['latestText'] = order.latestText
                record['id'] = order.id
                result.append(record)
        elif type == 'tmclist':
            orgId = request.GET.get('orgId', None)
            # 186 华北
            # 187 华南
            # 188 华东
            mapping = {
                '186': 'A1',
                '187': 'A3',
                '188': 'A2'
            }
            elasticAvailable = False
            com = getCurrentCompany()
            tmcs = BP.objects.filter(asBPB__bpA=com, asBPB__relation='TM', valid=True).all()
            if orgId:
                districtKey = mapping.get(orgId)
                tmcs = tmcs.filter(address1__district__key=districtKey)
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
        elif type == 'accountlist':
            pass
        elif type == 'report':
            # All statistic report goes here
            # Use parameter t - type c - category
            result = GetAJAXReport(request)
        elif type == 'salesmanlist':
            result = []
            orgIdList = []
            orgId = request.GET.get('orgId', None)
            if orgId:
                orgIdList.append(orgId)
            else:
                company = getCurrentCompany()
                # Get sales department, only 1 here and should be existing
                sdRel = BPRelation.objects.filter(bpA=company, relation='SD')
                if sdRel:
                    sdRel = sdRel[0]
                # Get the sales organization/area by the department
                orgRel = BPRelation.objects.filter(bpA=sdRel.bpB, relation='BL')
                for org in orgRel:
                    orgIdList.append(org.bpB.id)
            salesmanRel = BPRelation.objects.filter(bpA__id__in=orgIdList, relation='BL')
            for salesman in salesmanRel:
                # Get statistics by each salesman
                record = {}
                record['name'] = salesman.bpB.displayName()
                record['id'] = salesman.bpB.id
                # Get all sales order by the person
                saleOrders = Order.objects.filter(deleteFlag=False, type='SA01', orderpf__pf='00003',
                                                  orderpf__bp=salesman.bpB)
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
                    pendingRate = "%d ％" % ((float(pendingCount) / float(totalCount)) * 100)
                    onlineRate = "%d ％" % ((float(onlineCount) / float(totalCount)) * 100)
                else:
                    pendingRate = "0 ％"
                    onlineRate = "0 ％"
                record['pendingRate'] = pendingRate
                record['onlineRate'] = onlineRate
                record['totalCount'] = totalCount
                record['pendingCount'] = pendingCount
                record['onlineCount'] = onlineCount
                record['newOfMonthCount'] = newOfMonthCount
                result.append(record)
        elif type == 'salesmantxnlist':
            pass
        elif type == 'documentlist':
            fa = FileAttachment.objects.filter(deleteFlag=False)
            for f in fa:
                file = {}
                file['id'] = f.id
                file['name'] = f.file._get_path().split('/')[-1]
                file['description'] = f.description
                file['version'] = f.version
                result.append(file)
        elif type == 'customerbplist':
            result = customerModelService.getlist(None, None)
        elif type == 'mymessagelist':
            result = messageModelService.getlist(None, **{'request': request})
        elif type == 'myunreadmessagecount':
            ul = getCurrentUser(request)
            ul.pulseAt = datetime.datetime.now()
            ul.save()
            result = SiteMessage.objects.filter(receiver=ul, receiverReadFlag=False, receiverDeleteFlag=False).order_by("-sentAt").count()
        elif type == 'userlist':
            result = []
            com = getCurrentCompany()
            users = [ul for ul in UserLogin.objects.all()]
            for user in users:
                record={}
                record['userId']=user.id
                record['userBpName']=user.userbp.displayName()
                record['isAlive'] = user.isAlive()
                record['title'] = user.userbp.title
                record['mobile'] = user.userbp.mobile
                record['email'] = user.userbp.email
                result.append(record)
            # result.sort(lambda x, y: cmp(x['userBpName'], y['userBpName']))
        elif type == 'myworklist':
            result = []
            up = request.session.get('up', None)
            if up['loginRole'] == 'OPERATION_ROLE':
                orders = Order.objects.filter(Q(type='CK01'),Q(deleteFlag=False),~Q(ordercustomized__checkResult='E1003'))
                for order in orders:
                    record = {}
                    record['id'] = order.id
                    record['desc'] = order.description
                    empResp = OrderPFGetSingleBP(order, '00003')
                    if empResp:
                        record['empResp'] = empResp.displayName()
                    else:
                        record['empResp'] = ''
                    result.append(record)



        resp = json.dumps(result)
        return HttpResponse(resp)


def GetWeeklyReport(interval, option, request):
    result = []
    date = datetime.datetime.now() - datetime.timedelta(days=int(interval))
    if option == 'sleepaccount':
        pass
    elif option == 'online':
        orders = Order.objects.filter(type='SA01', updatedAt__gte=date, ordercustomized__stage='00006').order_by(
            "-updatedAt")
        for order in orders:
            record = {}
            record['id'] = order.id
            record['customer'] = order.description
            record['channel'] = ''
            channel = order.orderpf_set.filter(pf__key='00002')
            if channel:
                channel = channel[0]
                record['channel'] = channel.bp.displayName()
            record['salesman'] = OrderPFGetSingleBP(order, '00003').displayName()
            updatedAt = str(timezone.localtime(order.updatedAt).strftime("%Y-%m-%d %H:%M:%S"))
            record['updatedAt'] = updatedAt
            record['accountNumber'] = ''

            result.append(record)
    elif option == 'new':
        orders = Order.objects.filter(type='SA01', createdAt__gte=date).order_by("-updatedAt")
        for order in orders:
            record = {}
            record['id'] = order.id
            record['customer'] = order.description
            record['channel'] = ''
            channel = order.orderpf_set.filter(pf__key='00002')
            if channel:
                channel = channel[0]
                record['channel'] = channel.bp.displayName()
            record['salesman'] = OrderPFGetSingleBP(order, '00003').displayName()
            updatedAt = str(timezone.localtime(order.updatedAt).strftime("%Y-%m-%d %H:%M:%S"))
            record['updatedAt'] = updatedAt
            record['accountNumber'] = ''
            bp = OrderPFGetSingleBP(order, '00001')
            result.append(record)
    elif option == 'pending':
        orders = Order.objects.filter(type='SA01', updatedAt__gte=date, status__key='E0005').order_by("-updatedAt")
        for order in orders:
            record = {}
            record['id'] = order.id
            record['customer'] = order.description
            record['channel'] = ''
            channel = order.orderpf_set.filter(pf__key='00002')
            if channel:
                channel = channel[0]
                record['channel'] = channel.bp.displayName()
            record['salesman'] = OrderPFGetSingleBP(order, '00003').displayName()
            updatedAt = str(timezone.localtime(order.updatedAt).strftime("%Y-%m-%d %H:%M:%S"))
            record['updatedAt'] = updatedAt
            record['accountNumber'] = ''
            bp = OrderPFGetSingleBP(order, '00001')
            result.append(record)
    elif option == 'changes':
        changeHistory = ChangeHistory. \
            objects.filter(Q(type='Order'), Q(updatedAt__gte=date)).order_by("-updatedAt")
        for oh in changeHistory:
            record = {}
            updatedBy = BP.objects.get(id=oh.updatedBy).displayName()
            updatedAt = str(timezone.localtime(oh.updatedAt).strftime("%Y-%m-%d %H:%M:%S"))
            order = Order.objects.get(id=oh.objectId)
            if order.type.key != 'SA01':
                continue
            # chList['orderId'] = oh.orderId
            orderDesc = order.description
            record['id'] = order.id
            record['orderDesc'] = orderDesc
            record['orderField'] = getPhrase(request, 'order', oh.objectField)
            record['newValue'] = oh.newValue
            record['oldValue'] = oh.oldValue
            record['updatedBy'] = updatedBy
            record['updatedAt'] = updatedAt
            result.append(record)
    return result


@csrf_exempt
def tile(request):
    """
    This method returns html tile used to be embeded in other fragemnt
    :param request:
    :return:
    """
    if not checkIsUserLogin(request):
        resp = json.dumps('')
        return HttpResponse(resp)
    if request.method == 'GET':
        result = []
        type = request.GET.get('t', None)
        if type == 'salestagerpt':
            bpId = request.GET.get('bpId', None)
            if not bpId:
                return HttpResponse('')
            stageArray = ['00001', '00002', '00003', '00004', '00005', '00006']
            bp = BP.objects.get(id=bpId)
            saleOrders = Order.objects.filter(deleteFlag=False, type='SA01', orderpf__pf='00003', orderpf__bp=bp)
            nonPendingOrders = saleOrders.filter(~Q(status__key='E0005'))
            result = []
            for order in nonPendingOrders:
                # Get statistics for each order of this salesman
                stages = GetOrderStageStatistics(order.id, stageArray)
                resultDic = {}
                resultDic['desc'] = order.description
                resultDic['id'] = order.id
                resultDic['channel'] = ''
                channel = order.orderpf_set.filter(pf__key='00002')
                if channel:
                    channel = channel[0]
                    resultDic['channel'] = channel.bp.displayName()
                resultDic['travelAmount'] = order.ordercustomized.travelAmount
                resultDic['text'] = ''
                texts = order.ordertext_set.all()
                if texts:
                    texts = texts.order_by('-createdAt')
                    resultDic['text'] = texts[0].content
                resultDic['statistic'] = stages
                result.append(resultDic)
            template = loader.get_template('crm/tiles/salestagetile.html')
            tableId = GetRandomName('tab')
            context = RequestContext(request, {
                'tableId': tableId,
                'recordstatistic': result
            })
            return HttpResponse(template.render(context))
    return HttpResponse('')


def test(request, context):
    # sopt = getEChartOptionTemplate()
    #
    # rels = ['SD', 'OP', 'FI', 'HR', 'PD']
    # company = getCurrentCompany()
    # node = {'name': company.displayName(), 'value': '', 'children': []}
    # for rel in rels:
    #     bps = BPRelation.objects.filter(bpA=company, relation=rel)
    #     for bp in bps:
    #         subNode = {'name': bp.bpB.displayName(), 'value': '', 'children': []}
    #         getBPRel(subNode['children'], bp.bpB, 'BL')
    #         node['children'].append(subNode)
    # data = []
    # sopt['tooltip'] = {
    #     'trigger': 'item',
    #     'formatter': "{b}"
    # }
    # sopt['series'] = [
    #     {
    #         'name': u'树图',
    #         'type': 'tree',
    #         'orient': 'vertical',
    #         'rootLocation': {'x': 'center', 'y': 50},
    #         'nodePadding': 10,
    #         'layerPadding':60,
    #         'symbolSize': 20,
    #         'itemStyle': {
    #             'normal': {
    #                 'label': {
    #                     'show': 'true',
    #                     'formatter': "{a} {b} {c}"
    #                 },
    #                 'lineStyle': {
    #                     'color': '#48b',
    #                     'shadowColor': '#000',
    #                     'shadowBlur': 3,
    #                     'shadowOffsetX': 3,
    #                     'shadowOffsetY': 5,
    #                     'type': 'curve'
    #                     # // 'curve' | 'broken' | 'solid' | 'dotted' | 'dashed'
    #
    #                 }
    #             },
    #             'emphasis': {
    #                 'label': {
    #                     'show': 'true'
    #                 }
    #             }
    #         },
    #
    #         'data': [node]
    #     }]
    #
    # print sopt
    # context['stackOpt'] = json.dumps(sopt)
    return 'crm/test.html'

def message(request, context):
    com = getCurrentCompany()
    users = [ul for ul in UserLogin.objects.all()]
    context['users'] = users
    return 'crm/message.html'