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
    ['nickName', 'g_default', 'cn', u'昵称'],
    ['nickName', 'g_default', 'en', u'Nickname'],
    ['oldPassword', 'g_default', 'cn', u'旧密码'],
    ['oldPassword', 'g_default', 'en', u'Old password'],
    ['enterOldPwd', 'g_default', 'cn', u'输入旧密码'],
    ['enterOldPwd', 'g_default', 'en', u'Enter old password'],
    ['newPassword', 'g_default', 'cn', u'新密码'],
    ['newPassword', 'g_default', 'en', u'New password'],
    ['enterNewPwd', 'g_default', 'cn', u'输入密码'],
    ['enterNewPwd', 'g_default', 'en', u'Enter new password'],
    ['reNewPassword', 'g_default', 'cn', u'确认新密码'],
    ['reNewPassword', 'g_default', 'en', u'Confirm new password'],
    ['eNewPwdAgain', 'g_default', 'cn', u'再次输入新密码'],
    ['eNewPwdAgain', 'g_default', 'en', u'Enter new password again'],
    ['calEventColor', 'g_default', 'cn', u'日程项目颜色'],
    ['calEventColor', 'g_default', 'en', u'Calendar item color'],
    ['public', 'order', 'cn', u'公开'],
    ['public', 'order', 'en', u'Public'],
    ['content', 'order', 'cn', u'内容'],
    ['content', 'order', 'en', u'Detail'],
    ['title', 'order', 'cn', u'标题'],
    ['title', 'order', 'en', u'Title'],
    ['orderChart', 'order', 'cn', u'概览'],
    ['orderChart', 'order', 'en', u'Overview'],
    ['orderList', 'order', 'cn', u'列表'],
    ['orderList', 'order', 'en', u'List'],
    ['newText', 'bp', 'cn', u'新增备注'],
    ['newText', 'bp', 'en', u'New Text'],
    ['allText', 'bp', 'cn', u'全部备注'],
    ['allText', 'bp', 'en', u'All Text'],
    ['customerType', 'order', 'cn', u'账户类型'],
    ['customerType', 'order', 'en', u'Type'],
    ['settleType', 'order', 'cn', u'结算类型'],
    ['settleType', 'order', 'en', u'Settlement'],
    ['orderSaved', 'g_default', 'cn', u'数据已保存'],
    ['orderSaved', 'g_default', 'en', u'Order saved'],
    ['field', 'g_default', 'cn', u'字段'],
    ['field', 'g_default', 'en', u'Field'],
    ['oldValue', 'g_default', 'cn', u'旧值'],
    ['oldValue', 'g_default', 'en', u'Old Value'],
    ['newValue', 'g_default', 'cn', u'新值'],
    ['newValue', 'g_default', 'en', u'New Value'],
    ['updatedBy', 'g_default', 'cn', u'更新者'],
    ['updatedBy', 'g_default', 'en', u'Updated By'],
    ['updatedAt', 'g_default', 'cn', u'更新时间'],
    ['updatedAt', 'g_default', 'en', u'Updated At'],
    ['UATP', 'order', 'cn', u'UATP票'],
    ['UATP', 'order', 'en', u'UATP Tickets'],
    ['NONUATP', 'order', 'cn', u'非UATP票'],
    ['NONUATP', 'order', 'en', u'Non-UATP Tickets'],
    ['calendar', 'calendar', 'cn', u'日程'],
    ['calendar', 'calendar', 'en', u'Calendar'],
    ['detail', 'calendar', 'cn', u'详情'],
    ['detail', 'calendar', 'en', u'Activity'],
    ['startDateTime', 'order', 'cn', u'开始时间'],
    ['startDateTime', 'order', 'en', u'Start At'],
    ['endDateTime', 'order', 'cn', u'结束时间'],
    ['endDateTime', 'order', 'en', u'End At'],
    ['visibility', 'order', 'cn', u'可见性'],
    ['visibility', 'order', 'en', u'Visible'],
    ['upload', 'g_default', 'cn', u'上传'],
    ['upload', 'g_default', 'en', u'Upload'],
    ['addNewFile', 'g_default', 'cn', u'新增文件'],
    ['addNewFile', 'g_default', 'en', u'Add new file'],
    ['caution', 'g_default', 'cn', u'注意'],
    ['caution', 'g_default', 'en', u'Caution'],
    ['delFilePrompt', 'order', 'cn', u'确认要删除该文件吗？'],
    ['delFilePrompt', 'order', 'en', u'Are you sure to delete the file?'],
    ['thisYear', 'g_default', 'cn', u'本年'],
    ['thisYear', 'g_default', 'en', u'This year'],
    ['thisSeason', 'g_default', 'cn', u'本季度'],
    ['thisSeason', 'g_default', 'en', u'This season'],
    ['thisMonth', 'g_default', 'cn', u'本月'],
    ['thisMonth', 'g_default', 'en', u'This month'],
    ['thisWeek', 'g_default', 'cn', u'本周'],
    ['thisWeek', 'g_default', 'en', u'This week'],
    ['cardNumber', 'g_default', 'cn', u'卡号'],
    ['cardNumber', 'g_default', 'en', u'Card Number'],
    ['sales', 'g_default', 'cn', u'销售'],
    ['sales', 'g_default', 'en', u'Salesman'],
    ['corporate', 'g_default', 'cn', u'企业'],
    ['corporate', 'g_default', 'en', u'Corporation'],
    ['detail', 'g_default', 'cn', u'详情'],
    ['detail', 'g_default', 'en', u'Detail'],
    ['attachment', 'g_default', 'cn', u'附件'],
    ['attachment', 'g_default', 'en', u'Attachment'],
    ['change', 'g_default', 'cn', u'修改历史'],
    ['change', 'g_default', 'en', u'Change log'],
    ['custDate', 'g_default', 'cn', u'自定义日期段'],
    ['custDate', 'g_default', 'en', u'Custimized Date Range'],
    ['salesAnalysis', 'g_default', 'cn', u'销售业务分析'],
    ['salesAnalysis', 'g_default', 'en', u'Analysis'],
    ['all', 'g_default', 'cn', u'全部'],
    ['all', 'g_default', 'en', u'All'],
    ['transactionTotal', 'g_default', 'cn', u'交易量'],
    ['transactionTotal', 'g_default', 'en', u'Total'],
    ['shanhangTotal', 'g_default', 'cn', u'山航交易量'],
    ['shanhangTotal', 'g_default', 'en', u'Shanghan Total'],
    ['err.e01', 'g_default', 'cn', u'用户名或密码错误'],
    ['err.e01', 'g_default', 'en', u'Wrong username or password'],
    ['err.e02', 'g_default', 'cn', u'登录失败过多，账户已锁，请联系管理员'],
    ['err.e02', 'g_default', 'en', u'Too many failures, please contact administrator'],
    ['copyright', 'g_default', 'cn', u'&copy; 20XX-20XX 版权所有<br>'],
    ['copyright', 'g_default', 'en', u'&copy; 20XX-20XX'],
    ['version', 'g_default', 'cn', u'版本'],
    ['version', 'g_default', 'en', u'Version'],
    ['customerList', 'g_default', 'cn', u'客户列表'],
    ['customerList', 'g_default', 'en', u'Customers'],
    ['customerDetail', 'g_default', 'cn', u'客户详情'],
    ['customerDetail', 'g_default', 'en', u'Customer Detail'],
    ['phone', 'g_default', 'cn', u'联系电话'],
    ['phone', 'g_default', 'en', u'Phone'],
    ['contactPerson', 'g_default', 'cn', u'联系人'],
    ['contactPerson', 'g_default', 'en', u'Contact'],
    ['legalPerson', 'g_default', 'cn', u'法人'],
    ['legalPerson', 'g_default', 'en', u'Legal Person'],
    ['actualPerson', 'g_default', 'cn', u'实际控制人'],
    ['actualPerson', 'g_default', 'en', u'Actual Person'],
    ['copStructure', 'g_default', 'cn', u'组织结构'],
    ['copStructure', 'g_default', 'en', u'Structure'],
    ['corpLiscense', 'g_default', 'cn', u'营业执照'],
    ['corpLiscense', 'g_default', 'en', u'Liscense'],
    ['showLiscense', 'g_default', 'cn', u'显示'],
    ['showLiscense', 'g_default', 'en', u'Show'],
    ['noLiscense', 'g_default', 'cn', u'未上传'],
    ['noLiscense', 'g_default', 'en', u'Not available'],
    ['reUpload', 'g_default', 'cn', u'重新上传'],
    ['reUpload', 'g_default', 'en', u'Reupload'],
    ['searchOrder', 'bp', 'cn', u'筛选条件'],
    ['searchOrder', 'bp', 'en', u'Search'],
    ['type', 'bp', 'cn', u'类型'],
    ['type', 'bp', 'en', u'Type'],
    ['name1', 'bp', 'cn', u'名称 1'],
    ['name1', 'bp', 'en', u'Name 1'],
    ['name2', 'bp', 'cn', u'名称 2'],
    ['name2', 'bp', 'en', u'Name 2'],
    ['commonBp', 'menu', 'cn', u'商业伙伴'],
    ['commonBp', 'menu', 'en', u'Business Partner'],
    ['createBp', 'g_default', 'cn', u'创建商业伙伴'],
    ['createBp', 'g_default', 'en', u'Create Business Partner'],
    ['createBpTxt', 'g_default', 'cn', u'选择商业伙伴类型'],
    ['createBpTxt', 'g_default', 'en', u'Select business partner type'],
    ['bpSaved', 'g_default', 'cn', u'商业伙伴已保存'],
    ['bpSaved', 'g_default', 'en', u'Business partner saved'],
    ['district', 'bp', 'cn', u'地区'],
    ['district', 'bp', 'en', u'District'],
    ['phone', 'bp', 'cn', u'联系电话'],
    ['phone', 'bp', 'en', u'Phone'],
    ['contact', 'bp', 'cn', u'联系人'],
    ['contact', 'bp', 'en', u'Contact'],
    ['legalPerson', 'bp', 'cn', u'法人'],
    ['legalPerson', 'bp', 'en', u'Legal Person'],
    ['actualPerson', 'bp', 'cn', u'实际控制人'],
    ['actualPerson', 'bp', 'en', u'Actual Person'],
    ['corpStructure', 'bp', 'cn', u'组织结构'],
    ['corpStructure', 'bp', 'en', u'Corporation type'],
    ['partnerNo', 'bp', 'cn', u'编号'],
    ['partnerNo', 'bp', 'en', u'Partner No'],
    ['id', 'bp', 'cn', u'编号'],
    ['id', 'bp', 'en', u'ID'],
    ['corpLiscense', 'bp', 'cn', u'营业执照'],
    ['corpLiscense', 'bp', 'en', u'Liscense'],
    ['noImage', 'g_default', 'cn', u'未上传图片'],
    ['noImage', 'g_default', 'en', u'No image'],
    ['noFile', 'g_default', 'cn', u'未上传文件'],
    ['noFile', 'g_default', 'en', u'No file'],
    ['err.noRole', 'g_default', 'cn', u"""您还未被指派角色，请联系管理员"""],
    ['err.noRole', 'g_default', 'en', u"""You don't have role assigned yet, please contact administrator"""],
    ['file1', 'order', 'cn', u'文件1'],
    ['file1', 'order', 'en', u'File 1'],
    ['imgFile1', 'order', 'cn', u'图片1'],
    ['imgFile1', 'order', 'en', u'Image 1'],
    ['file2', 'order', 'cn', u'文件2'],
    ['file2', 'order', 'en', u'File 2'],
    ['imgFile2', 'order', 'cn', u'图片2'],
    ['imgFile2', 'order', 'en', u'Image 2'],
    ['file1', 'bp', 'cn', u'文件1'],
    ['file1', 'bp', 'en', u'File 1'],
    ['imgFile1', 'bp', 'cn', u'图片1'],
    ['imgFile1', 'bp', 'en', u'Image 1'],
    ['file2', 'bp', 'cn', u'文件2'],
    ['file2', 'bp', 'en', u'File 2'],
    ['imgFile2', 'bp', 'cn', u'图片2'],
    ['imgFile2', 'bp', 'en', u'Image 2'],
    ['feedback', 'g_default', 'cn', u'我有意见'],
    ['feedback', 'g_default', 'en', u'Feedback'],
    ['feedback', 'menu', 'cn', u'我有意见'],
    ['feedback', 'menu', 'en', u'Feedback'],
    ['message', 'menu', 'cn', u'消息'],
    ['message', 'menu', 'en', u'Message'],
    ['sender', 'message', 'cn', u'发送者'],
    ['sender', 'message', 'en', u'Sender'],
    ['receiver', 'message', 'cn', u'接收者'],
    ['receiver', 'message', 'en', u'Receiver'],
    ['content', 'message', 'cn', u'内容'],
    ['content', 'message', 'en', u'Content'],
    ['sentAt', 'message', 'cn', u'时间'],
    ['sentAt', 'message', 'en', u'Sent At'],
    ['orderFollowUp', 'g_default', 'cn', u'相关单据'],
    ['orderFollowUp', 'g_default', 'en', u'Follow ups'],
    ['createFollowUp', 'g_default', 'cn', u'创建跟进'],
    ['createFollowUp', 'g_default', 'en', u'Follow up'],
    ['checkResult', 'order', 'cn', u'审核结果'],
    ['checkResult', 'order', 'en', u'Result'],
    ['err.inMaint', 'g_default', 'cn', u"""系统正在维护中，请稍后登录……"""],
    ['err.inMaint', 'g_default', 'en', u'Maintainence is ongoing, please wait...'],
    ['err.e03', 'g_default', 'cn', u"""该账号已被禁用"""],
    ['err.e03', 'g_default', 'en', u"""Account not valid"""],
    ['ajaxError', 'g_default', 'cn', u"""消息错误，请确保登录状态后重试"""],
    ['ajaxError', 'g_default', 'en', u"""Response error"""],
    ['title', 'feedback', 'cn', u"""标题"""],
    ['title', 'feedback', 'en', u"""Title"""],
    ['type', 'feedback', 'cn', u"""类型"""],
    ['type', 'feedback', 'en', u"""Type"""],
    ['text', 'feedback', 'cn', u"""详细意见"""],
    ['text', 'feedback', 'en', u"""Text"""],
    ['bug', 'feedback', 'cn', u"""Bug错误"""],
    ['bug', 'feedback', 'en', u"""Bug"""],
    ['suggestion', 'feedback', 'cn', u"""需求建议"""],
    ['suggestion', 'feedback', 'en', u"""New requirement"""],
    ['corpStruct', 'menu', 'cn', u"""公司结构"""],
    ['corpStruct', 'menu', 'en', u"""Sturcture"""],
    ['corpStruct', 'g_default', 'cn', u"""公司结构"""],
    ['corpStruct', 'g_default', 'en', u"""Sturcture"""],
    ['myWork', 'menu', 'cn', u'我的任务'],
    ['myWork', 'menu', 'en', u'My work'],
    ['checkOrder', 'order', 'cn', u'审核对象'],
    ['checkOrder', 'order', 'en', u'Check target'],
    ['reply', 'g_default', 'cn', u'回复'],
    ['reply', 'g_default', 'en', u'Reply'],
    ['text', 'message', 'cn', u'内容'],
    ['text', 'message', 'en', u'Content'],
    ['send', 'message', 'cn', u'发送'],
    ['send', 'message', 'en', u'Send'],
    ['sendMessage', 'message', 'cn', u'发送消息'],
    ['sendMessage', 'message', 'en', u'Post'],
    ['dataTableCommNoPro', 'g_default', 'cn', None, u"""
            "sDom": "<'row'<'col-md-6'l><'col-md-6'f>r>t<'row'<'col-md-12'i><'col-md-12 center-block'p>>", "sPaginationType": "bootstrap", "oLanguage": { "sLengthMenu": "每页 _MENU_ 条记录", "oPaginate": { "sFirst": "首页", "sLast": "末页", "sNext": "下一页", "sPrevious": "上一页" }, "sEmptyTable": "无记录", "sInfo": "共 _TOTAL_ 条记录 (_START_ ／ _END_)", "sInfoEmpty": "无记录", "sSearch": "快速搜索 _INPUT_ ", "sZeroRecords": "无匹配记录", "sInfoFiltered": "从 _MAX_ 条记录中过滤","sProcessing": ""},
            """],
    ['dataTableCommNoPro', 'g_default', 'en', None, u"""
            "sDom": "<'row'<'col-md-6'l><'col-md-6'f>r>t<'row'<'col-md-12'i><'col-md-12 center-block'p>>", "sPaginationType": "bootstrap", "oLanguage": { "sLengthMenu": "_MENU_ Per page", "oPaginate": { "sFirst": "First", "sLast": "Last", "sNext": "Next", "sPrevious": "Previous" }, "sEmptyTable": "No record", "sInfo": "Total _TOTAL_ record(s) (_START_ ／ _END_)", "sInfoEmpty": "No records", "sSearch": "Fast search _INPUT_ ", "sZeroRecords": "No record matches", "sInfoFiltered": "Filter from _MAX_ record(s)","sProcessing": ""},
            """
     ],
    ['dev', 'menu', 'cn', u'开发'],
    ['dev', 'menu', 'en', u'Develop'],
    ['add', 'g_default', 'cn', u'增加'],
    ['add', 'g_default', 'en', u'Add']
]

for phrase in phrases:
    print phrase
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
