# -*- coding: UTF-8 -*-
import os, django

os.environ['DJANGO_SETTINGS_MODULE'] = 'crm_site.settings'
django.setup()

from crm.models import *
from crm.common import *

# Demo initialize
# UserRoleType
userRoleTypes = [
    ['SALES_ROLE', u"销售"],
    ['DEV_ROLE', u"CRM开发"]
]

for userRoleType in userRoleTypes:
    p = {}
    p['key'] = userRoleType[0]
    p['description'] = userRoleType[1]
    UserRoleType.objects.update_or_create(**p)

# ViewType
viewTypes = [
    ['Search', u"Search View"],
    ['Result', u"Result View"],
    ['Detail', u"Detail View"]
]

for viewType in viewTypes:
    p = {}
    p['key'] = viewType[0]
    p['description'] = viewType[1]
    ViewType.objects.update_or_create(**p)

# SiteLanguage
siteLanguages = [
    ['en', u"English"],
    ['cn', u"中文"]
]

for siteLanguage in siteLanguages:
    p = {}
    p['key'] = siteLanguage[0]
    p['description'] = siteLanguage[1]
    SiteLanguage.objects.update_or_create(**p)

# SiteMenuItem
siteMenuItems = [
    ['SALES_ROLE', None, 'home', 'menu', 'home', 10, True],
    ['SALES_ROLE', None, 'comSearch', 'menu', 'commonOrder', 20, True]
]

for siteMenuItem in siteMenuItems:
    p = {}
    p['role'] = UserRoleType.objects.get(pk=siteMenuItem[0])
    p['parentMenuId'] = siteMenuItem[1]
    p['phraseId'] = siteMenuItem[2]
    p['appId'] = siteMenuItem[3]
    p['pageApp'] = siteMenuItem[4]
    p['sortOrder'] = siteMenuItem[5]
    p['valid'] = siteMenuItem[6]
    SiteMenuItem.objects.update_or_create(**p)

# SiteMenuItem
siteAppTypes = [
    ['order', u"单据"],
    ['message', u"消息"],
    ['menu', u"菜单"],
    ['g_default', u"全局默认"],
    ['feedback', u"反馈"],
    ['calendar', u"日程"],
    ['bp', u"商业伙伴"]
]

for siteAppType in siteAppTypes:
    p = {}
    p['appId'] = siteAppType[0]
    p['description'] = siteAppType[1]
    SiteAppType.objects.update_or_create(**p)

userProfileTypes = [
    ['P_SALE_BASIC', 'Sales basic profile']
]
for userProfileType in userProfileTypes:
    p = {}
    p['key'] = userProfileType[0]
    p['description'] = userProfileType[1]
    UserProfileType.objects.update_or_create(**p)

authObjectTypes = [
    ['Order_SA01_Access', 'For order type SA01'],
    ['Order_AC01_Access', 'For order type AC01'],
    ['BP_OR_Access', 'For organization access'],
    ['BP_IN_Access', 'For individual account access'],
    ['BP_CO_Access', 'For corporation accounts access']
]
for authObjectType in authObjectTypes:
    p = {}
    p['key'] = authObjectType[0]
    p['description'] = authObjectType[1]
    AuthObjectType.objects.update_or_create(**p)

orderBaseTypes = [
    ['Order', 'Order'],
    ['Activity', 'Activity']
]
for orderBaseType in orderBaseTypes:
    p = {}
    p['key'] = orderBaseType[0]
    p['description'] = orderBaseType[1]
    OrderBaseType.objects.update_or_create(**p)

orderTypes = [
    ['SA01', 'Order', u'销售线索', 'attachment,changelog'],
    ['AC01', 'Activity', u'日程活动', '']
]
for orderType in orderTypes:
    p = {}
    p['key'] = orderType[0]
    p['baseType'] = OrderBaseType.objects.get(pk=orderType[1])
    p['description'] = orderType[2]
    p['assignmentBlock'] = orderType[3]
    OrderType.objects.update_or_create(**p)

orderBEDefs = [
    ['SA01', 'SaleOrderBE'],
    ['AC01', 'ActivityBE']
]
for orderBEDef in orderBEDefs:
    p = {}
    p['orderType'] = OrderType.objects.get(pk=orderBEDef[0])
    p['businessEntity'] = orderBEDef[1]
    OrderBEDef.objects.update_or_create(**p)

addressTypes = [
    ['ST', u'默认地址']
]
for addressType in addressTypes:
    p = {}
    p['key'] = addressType[0]
    p['description'] = addressType[1]
    AddressType.objects.update_or_create(**p)

bPTypes = [
    ['ZZ', None, u'本公司', None],
    ['OR', None, u'部门组织', None],
    ['IN', None, u'个人账户', None],
    ['CO', None, u'公司账户', None]
]
for bPType in bPTypes:
    p = {}
    p['key'] = bPType[0]
    p['baseType'] = None
    p['description'] = bPType[2]
    p['assignmentBlock'] = None
    BPType.objects.update_or_create(**p)

userLoginStatuses = [
    ['LOCK', u'已锁'],
    ['CLOSED', u'关闭'],
    ['ACTIVE', u'正常']
]
for userLoginStatus in userLoginStatuses:
    p = {}
    p['key'] = userLoginStatus[0]
    p['description'] = userLoginStatus[1]
    UserLoginStatus.objects.update_or_create(**p)



# tester user
firstName = 'tester'
lastName = 'tester'
bp = BP.objects.filter(firstName=firstName, lastName=lastName)
if bp:
    bp = bp[0]
else:
    bp = BP()
bp.type = BPType.objects.get(pk='IN')
bp.firstName = firstName
bp.lastName = lastName
bp.save()

userLogin = UserLogin.objects.filter(userbp=bp)
if userLogin:
    userLogin = userLogin[0]
else:
    userLogin = UserLogin()
    user = User()
    user.nickName = '%s %s' % (lastName, firstName)
    user.realName = '%s %s' % (lastName, firstName)
    user.save()
    userLogin.user = user
    userLogin.userbp = bp

    userLogin.username = "%s.%s" % (firstName, lastName)
    userLogin.password = '111111'
    userLogin.passwordEncrypted = False
    userLogin.status = UserLoginStatus.objects.get(pk='ACTIVE')
    userLogin.save()

    userRole = UserRole()
    userRole.userlogin = userLogin
    userRole.role = UserRoleType.objects.get(pk='SALES_ROLE')
    userRole.save()

# Phrases
phrases = [
    ['dataTableCommNoPro', 'g_default', 'cn', None, u"""
    "sDom": "<'row'<'col-md-6'l><'col-md-6'f>r>t<'row'<'col-md-12'i><'col-md-12 center-block'p>>", "sPaginationType": "bootstrap", "oLanguage": { "sLengthMenu": "每页 _MENU_ 条记录", "oPaginate": { "sFirst": "首页", "sLast": "末页", "sNext": "下一页", "sPrevious": "上一页" }, "sEmptyTable": "无记录", "sInfo": "共 _TOTAL_ 条记录 (_START_ ／ _END_)", "sInfoEmpty": "无记录", "sSearch": "快速搜索 _INPUT_ ", "sZeroRecords": "无匹配记录", "sInfoFiltered": "从 _MAX_ 条记录中过滤","sProcessing": ""},
    """],
    ['dataTableCommNoPro', 'g_default', 'en', None, u"""
    "sDom": "<'row'<'col-md-6'l><'col-md-6'f>r>t<'row'<'col-md-12'i><'col-md-12 center-block'p>>", "sPaginationType": "bootstrap", "oLanguage": { "sLengthMenu": "_MENU_ Per page", "oPaginate": { "sFirst": "First", "sLast": "Last", "sNext": "Next", "sPrevious": "Previous" }, "sEmptyTable": "No record", "sInfo": "Total _TOTAL_ record(s) (_START_ ／ _END_)", "sInfoEmpty": "No records", "sSearch": "Fast search _INPUT_ ", "sZeroRecords": "No record matches", "sInfoFiltered": "Filter from _MAX_ record(s)","sProcessing": ""},
    """
     ]
]

for phrase in phrases:
    p = {}
    p['phraseId'] = phrase[0]
    p['app'] = SiteAppType.objects.get(appId=phrase[1])
    p['phraseLan'] = SiteLanguage.objects.get(key=phrase[2])
    if phrase[3]:
        p['content'] = phrase[3]
    else:
        p['content'] = ''
        p['bigContent'] = phrase[4]
    SitePhrase.objects.update_or_create(**p)
