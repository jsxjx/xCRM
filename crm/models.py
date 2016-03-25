# -*- coding: UTF-8 -*-

from django.db import models
from django import forms
from django.forms import ModelForm, Form
import sys
import datetime
from django.utils import timezone

reload(sys)
sys.setdefaultencoding("utf-8")


# User
# This table used to store user information for the site
# Because I don't want this framework to be only used as CRM system
# It should cost little to change into another system, for future
class User(models.Model):
    nickName = models.CharField(max_length=50, verbose_name=u"昵称")
    realName = models.CharField(max_length=50, verbose_name=u"姓名")

    def __unicode__(self):
        return "%s:%s" % (self.nickName, self.realName)

    class Meta:
        verbose_name = u"用户信息"
        verbose_name_plural = u"用户信息"


# This table defines user login status
# ACTIVE or LOCK for example
class UserLoginStatus(models.Model):
    key = models.CharField(max_length=20, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"用户登录状态"
        verbose_name_plural = u"用户登录状态"


# This table stores user login information, username/password etc
# The table also refer a userBp object, since either user could be one of the person who
# use this CRM system, or other person irrelated to system, like, visitor.
class UserLogin(models.Model):
    username = models.CharField(max_length=30, verbose_name=u"用户名")
    password = models.CharField(max_length=100, verbose_name=u"密码")
    user = models.OneToOneField('User', verbose_name=u"用户信息实体")
    userbp = models.OneToOneField('BP', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u"用户实体")
    passwordEncrypted = models.BooleanField(default=False, verbose_name=u"已加密")
    status = models.ForeignKey('UserLoginStatus', null=True, blank=True, verbose_name=u"状态")
    failureCount = models.IntegerField(default=0, verbose_name=u"失败次数")
    lastLoginAt = models.DateTimeField(null=True, blank=True, verbose_name=u"最后登录时间")
    pulseAt = models.DateTimeField(null=True, blank=True, verbose_name=u"最后心跳时间")

    def __unicode__(self):
        return "%s %s %s" % (self.username, self.user.nickName, self.user.realName)

    def isAlive(self):
        if self.pulseAt:
            diff = datetime.datetime.utcnow().replace(tzinfo=timezone.utc) - self.pulseAt
            return bool(diff.seconds <= 10)
        else:
            return False

    class Meta:
        verbose_name = u"用户登录信息"
        verbose_name_plural = u"用户登录信息"


# Authorization object
# This table defines authorization for each object
# Authorization basically mean Create/Read(View)/Update(Change)/Delete(remove)
# Any object should or can be controlled by these 4 status
class AuthObject(models.Model):
    authObject = models.ForeignKey('AuthObjectType', verbose_name=u"权限对象类型")
    create = models.BooleanField(default=False, verbose_name=u"可创建")
    read = models.BooleanField(default=False, verbose_name=u"可查看")
    update = models.BooleanField(default=False, verbose_name=u"可更新")
    delete = models.BooleanField(default=False, verbose_name=u"可删除")

    def __unicode__(self):
        return "%s %s : C(%s) R(%s) U(%s) D(%s)" % (
            self.id, self.authObject, self.create, self.read, self.update, self.delete)

    class Meta:
        verbose_name = u"权限对象"
        verbose_name_plural = u"权限对象"


# Authorization object type
# This table defines authorization object type, or name for short.
class AuthObjectType(models.Model):
    key = models.CharField(max_length=20, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"权限对象类型"
        verbose_name_plural = u"权限对象类型"


# User role
# This table defines user role of the site
# Like Sales/Operation/Admin/Developer etc
class UserRoleType(models.Model):
    key = models.CharField(max_length=50, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"用户角色类型"
        verbose_name_plural = u"用户角色类型"


# This table defines user role, each user can have multiple roles
# It refer to UserLogin object because a user may not have related BP record
# E.g a temporarily visitor
class UserRole(models.Model):
    userlogin = models.ForeignKey('UserLogin', verbose_name=u"用户登录信息")
    role = models.ForeignKey('UserRoleType', verbose_name=u"用户角色类型")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")

    class Meta:
        verbose_name = u"用户角色"
        verbose_name_plural = u"用户角色"


# This table defines user profile type, or name for short
# A user profile is something to be assigned to user in order to
# inherit a bunch of authorizations
class UserProfileType(models.Model):
    key = models.CharField(max_length=50, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")
    # authObjects = models.ManyToManyField('AuthObject', null=True, blank=True)
    # authObjects = models.ForeignKey('AuthObject', null=True, blank=True)
    def __unicode__(self):
        return "%s %s" % (self.key, self.description)
        # return "%s (%s):%s" % (self.key, self.description, self.authObjects.all())
        # return "%s (%s):%s" % (self.key, self.description, self.authObjects)

    class Meta:
        verbose_name = u"用户配置文件类型"
        verbose_name_plural = u"用户配置文件类型"


# This table defines relationship between profile and authorization objects
# Means a single profile can have multiple authorizations, with a validity field
# Todo could add a time range for the validity, in case future needs
class UserProfileAuthObject(models.Model):
    profile = models.ForeignKey('UserProfileType', verbose_name=u"用户配置文件")
    singleAuthObject = models.ForeignKey('AuthObject', null=True, blank=True, verbose_name=u"权限对象类型")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")

    class Meta:
        verbose_name = u"用户配置文件对应权限对象"
        verbose_name_plural = u"用户配置文件对应权限对象"


# This table assigns profile to user
# Each user could have multiple profile, with validity field
# Todo could add a time range for the validity, in case future needs
class UserProfile(models.Model):
    userlogin = models.ForeignKey('UserLogin', verbose_name=u"用户登录信息")
    profile = models.ForeignKey('UserProfileType', verbose_name=u"用户配置文件类型")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")

    class Meta:
        verbose_name = u"用户配置文件"
        verbose_name_plural = u"用户配置文件"


# User Parameter
# This table stores user specified parameter for the site
# The parameter is mostly related to user setting, like customized skin etc
class UserParameter(models.Model):
    userlogin = models.ForeignKey('UserLogin', verbose_name=u"用户登录信息")
    name = models.CharField(max_length=50, verbose_name=u"名称")
    value = models.CharField(max_length=50, verbose_name=u"值")

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.value)

    class Meta:
        verbose_name = u"用户参数"
        verbose_name_plural = u"用户参数"


# This table stores single authorization assigned to user
# It mainly for the situation that you want user have some access temporarily
# and to be removed shortly after
class UserSingleAuthObject(models.Model):
    userlogin = models.ForeignKey('UserLogin', verbose_name=u"用户登录信息")
    singleAuthObject = models.ForeignKey('AuthObject', null=True, blank=True, verbose_name=u"权限对象类型")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")

    class Meta:
        verbose_name = u"用户权限对象"
        verbose_name_plural = u"用户权限对象"


# CRM tables
# This table stores Business Partner information
# A business partner is someone or an entity that company work with, it could be
# employee, customer, contacter, supplier, no matter what business/industry you are doing
# The main design is to reduce specified tables and provide cross industry solution
# This is my idea and purpose, don't listen to those stupid verdammte techless person
# and driven by them :)
class BP(models.Model):
    partnerNo = models.IntegerField(null=True, blank=True, verbose_name=u"伙伴编号")
    type = models.ForeignKey('BPType', verbose_name=u"伙伴类型")
    firstName = models.CharField(max_length=50, blank=True, verbose_name=u"名")
    middleName = models.CharField(max_length=50, blank=True, verbose_name=u"中间名")
    lastName = models.CharField(max_length=50, blank=True, verbose_name=u"姓")
    name1 = models.CharField(max_length=255, blank=True, verbose_name=u"名称1")
    name2 = models.CharField(max_length=255, blank=True, verbose_name=u"名称2")
    name3 = models.CharField(max_length=255, blank=True, verbose_name=u"名称3")
    name4 = models.CharField(max_length=255, blank=True, verbose_name=u"名称4")
    address1 = models.OneToOneField('Address', related_name='asAddress1Bp', null=True, blank=True, verbose_name=u"地址1")
    address2 = models.OneToOneField('Address', related_name='asAddress2Bp', null=True, blank=True, verbose_name=u"地址2")
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"头衔")
    mobile = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"联系手机")
    email = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"联系邮箱")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")
    # bpImg = models.ImageField(upload_to='bpAttachments', null=True, blank=True, verbose_name=u"伙伴图片")
    deleteFlag = models.BooleanField(default=False, verbose_name=u"删除标记")

    def displayName(self):
        name = ''
        if self.type.key == 'IN':
            name = "%s %s" % (self.lastName, self.firstName)
        else:
            name = self.name1
        return name

    def __unicode__(self):
        return "%s %s %s %s %s %s %s %s %s %s" % (
            self.id, self.type, self.firstName, self.middleName, self.lastName, self.name1, self.name2, self.name3,
            self.name4, self.valid)

    class Meta:
        verbose_name = u"商业伙伴"
        verbose_name_plural = u"商业伙伴"


# This table defines base BP types
# The table determined how it will be processed
class BPBaseType(models.Model):
    key = models.CharField(max_length=10, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"商业伙伴基本类型定义"
        verbose_name_plural = u"商业伙伴基本类型定义"


# This table defines BP type
# Combined with BP base type above looks enough
# E.g
# Base type: corporation   Base type: corporation
#      type: customer           type: supplier
# customer and supplier can share same process(detemined by base type) but special
# process itself(by type)
class BPType(models.Model):
    key = models.CharField(max_length=2, primary_key=True, verbose_name=u"主键")
    baseType = models.ForeignKey('BPBaseType', null=True, blank=True, verbose_name=u"基本类型")
    description = models.CharField(max_length=255, verbose_name=u"描述")
    assignmentBlock = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"扩展框")

    def __unicode__(self):
        return "%s(%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"商业伙伴类型"
        verbose_name_plural = u"商业伙伴类型"


# BP relationship type
# This table define relationship type, or name
class BPRelType(models.Model):
    key = models.CharField(max_length=2, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")
    descAtoB = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"A对B关系名称")
    descBtoA = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"B对A关系名称")

    def __unicode__(self):
        return "%s(%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"商业伙伴关系类型"
        verbose_name_plural = u"商业伙伴关系类型"


# This table store relationship between 2 business partner
# The idea is simple that "who has what relationship with who"
# The table is used to describe all relationship among the BPs within company
class BPRelation(models.Model):
    bpA = models.ForeignKey('BP', related_name='asBPA', verbose_name=u"伙伴A")
    bpB = models.ForeignKey('BP', related_name='asBPB', verbose_name=u"伙伴B")
    relation = models.ForeignKey('BPRelType', verbose_name=u"伙伴关系类型")
    comments = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"备注")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")

    def __unicode__(self):
        return "%s %s %s" % (self.bpA, unicode(self.relation.description), self.bpB)

    class Meta:
        verbose_name = u"商业伙伴关系"
        verbose_name_plural = u"商业伙伴关系"


# Extra fields for BP
# This table is a extra table for BP, it shall change base on special needs
# Any change on business is limited to XXCustomized table (XX=Order, BP)
# Todo Should it be a common table?
class BPCustomized(models.Model):
    bp = models.OneToOneField('BP', verbose_name=u"伙伴对象")
    # Touched
    boolAttribute1 = models.BooleanField(default=False, verbose_name=u"是否触达")
    # Signed
    boolAttribute2 = models.BooleanField(default=False, verbose_name=u"是否签约")
    # System connected
    boolAttribute3 = models.BooleanField(default=False, verbose_name=u"是否对接")
    # Employee Responsible
    empResp = models.ForeignKey('BP', related_name='corpEmpResp', null=True, blank=True, verbose_name=u"负责人")
    # Legal person
    legalPerson = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"法人")
    # Actual person
    actualPerson = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"实际控制人")
    # Corporation structure
    corpStructure = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"组织结构")
    # Corporation liscense
    corpLiscense = models.ImageField(upload_to='bpAttachments', null=True, blank=True, verbose_name=u"营业执照附件")
    # For extra usage
    file1 = models.FileField(upload_to='bpAttachments', null=True, blank=True, verbose_name=u"附件1")
    file2 = models.FileField(upload_to='bpAttachments', null=True, blank=True, verbose_name=u"附件2")
    imgFile1 = models.ImageField(upload_to='bpAttachments', null=True, blank=True, verbose_name=u"图片1")
    imgFile2 = models.ImageField(upload_to='bpAttachments', null=True, blank=True, verbose_name=u"图片2")

    def __unicode__(self):
        return "%s %s %s %s" % (self.bp, self.boolAttribute1, self.boolAttribute2, self.boolAttribute3)

    class Meta:
        verbose_name = u"商业伙伴扩展表"
        verbose_name_plural = u"商业伙伴扩展表"


# This table defines address type
# E.g. Standard address, Home address, delivery address etc base on needs
class AddressType(models.Model):
    key = models.CharField(max_length=2, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"地址类型"
        verbose_name_plural = u"地址类型"


# This table defines district type
# E.g. area, province etc based on needs
class DistrictType(models.Model):
    key = models.CharField(max_length=2, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"地区类型"
        verbose_name_plural = u"地区类型"


# This table stores address information
class Address(models.Model):
    type = models.ForeignKey('AddressType', verbose_name=u"地址类型")
    district = models.ForeignKey('DistrictType', null=True, blank=True, verbose_name=u"地区类型")
    address1 = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"地址1")
    address2 = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"地址2")
    address3 = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"地址3")
    address4 = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"地址4")
    phone1 = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"电话1")
    contact1 = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"联系人1")
    phone2 = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"电话2")
    contact2 = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"联系人2")

    def __unicode__(self):
        return "%s (%s %s %s %s %s %s %s)" % (
            self.type, self.district, self.address1, self.address2, self.address3, self.address4, self.phone1,
            self.phone2)

    class Meta:
        verbose_name = u"地址"
        verbose_name_plural = u"地址"


# This table defines base order type, name
class OrderBaseType(models.Model):
    key = models.CharField(max_length=10, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"单据基本类型定义"
        verbose_name_plural = u"单据基本类型定义"


# This table defines order type
# The design is same as BP, that base type and type determines how order is processed
class OrderType(models.Model):
    key = models.CharField(max_length=4, primary_key=True, verbose_name=u"主键")
    baseType = models.ForeignKey('OrderBaseType', verbose_name=u"基本类型")
    description = models.CharField(max_length=255, verbose_name=u"描述")
    assignmentBlock = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"扩展框")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"单据类型定义"
        verbose_name_plural = u"单据类型定义"


# This table defines relationship type between orders
# E.g. Order A 'has an item' Order B
#      Order A 'has a follow up'  Order B
class OrderRelType(models.Model):
    key = models.CharField(max_length=2, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")
    descAtoB = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"A对B关系名称")
    descBtoA = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"B对A关系名称")

    def __unicode__(self):
        return "%s(%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"单据关系类型"
        verbose_name_plural = u"单据关系类型"


class OrderRelation(models.Model):
    orderA = models.ForeignKey('Order', related_name='asOrderA', verbose_name=u"单据A")
    orderB = models.ForeignKey('Order', related_name='asOrderB', verbose_name=u"单据B")
    relation = models.ForeignKey('OrderRelType', verbose_name=u"单据关系类型")
    comments = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"备注")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")

    def __unicode__(self):
        return "%s %s %s" % (self.orderA, unicode(self.relation.description), self.orderB)

    class Meta:
        verbose_name = u"单据关系"
        verbose_name_plural = u"单据关系"


# Partner function type, define relationship type with BP
# E.g
# Z001 Customer
# Z002 Channel
# It's similar to BP relationship name, but partner function type defines what role
# a business partner is playing in an order
class PFType(models.Model):
    orderType = models.ForeignKey('OrderType', verbose_name=u"单据类型")
    key = models.CharField(max_length=5, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")
    # minimum number of partner function
    minimum = models.IntegerField(null=True, blank=True, verbose_name=u"最小出现次数")
    # maximum number of partner function
    maximum = models.IntegerField(null=True, blank=True, verbose_name=u"最大出现次数")

    class Meta:
        db_table = 'sales_PFType'
        unique_together = ("orderType", "key")
        verbose_name = u"合作伙伴关联类型定义"
        verbose_name_plural = u"合作伙伴关联类型定义"

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)


# Priority type
# This table defines priority for each order type
class PriorityType(models.Model):
    orderType = models.ForeignKey('OrderType', verbose_name=u"单据类型")
    key = models.CharField(max_length=5, verbose_name=u"主键")
    description = models.CharField(max_length=50, verbose_name=u"描述")
    sortOrder = models.IntegerField(null=True, blank=True, verbose_name=u"排序号")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"优先级定义"
        verbose_name_plural = u"优先级"


# Status type
# This table defines status type for each order
class StatusType(models.Model):
    orderType = models.ForeignKey('OrderType', verbose_name=u"单据类型")
    key = models.CharField(max_length=5, verbose_name=u"主键")
    description = models.CharField(max_length=50, verbose_name=u"描述")
    sortOrder = models.IntegerField(null=True, blank=True, verbose_name=u"排序号")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"状态定义"
        verbose_name_plural = u"状态定义"


# This table defines a extra selection field for order
# The purpose is to allow configuration on those selection fields rather than hardcoded
# You can dynamically add options to meet business requirement without deploy anything
# Any hardcoded emulation is stupid :)
class OrderExtSelectionFieldType(models.Model):
    orderType = models.ForeignKey('OrderType', verbose_name=u"单据类型")
    fieldKey = models.CharField(max_length=5, verbose_name=u"字段主键")
    key = models.CharField(max_length=50, verbose_name=u"主键")
    description = models.CharField(max_length=50, verbose_name=u"描述")
    sortOrder = models.IntegerField(null=True, blank=True, verbose_name=u"排序号")

    def __unicode__(self):
        return "%s %s (%s)" % (self.orderType.description, self.key, self.description)

    class Meta:
        verbose_name = u"单据选项字段定义"
        verbose_name_plural = u"单据选项字段定义"


# Text type
# This table defines text type(name) for an order
# A text type is used to describe what text it is.
# E.g "customer reply", "doctor scripts" "salesman comments"
class TextType(models.Model):
    orderType = models.ForeignKey('OrderType', verbose_name=u"单据类型")
    key = models.CharField(max_length=4, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"文本类型定义"
        verbose_name_plural = u"文本类型定义"


# BP Text type
# The table defines text type for BP, similar to order text type
class BPTextType(models.Model):
    bpType = models.ForeignKey('BPType', verbose_name=u"伙伴类型")
    key = models.CharField(max_length=4, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"商业伙伴文本类型定义"
        verbose_name_plural = u"商业伙伴文本类型定义"


# Order table
# This table stores orders(transactional records) for business needs
# An order record is anything company want to record
# E.g. a sales record, a repair record, a development task, a leaving request etc
class Order(models.Model):
    type = models.ForeignKey('OrderType', verbose_name=u"单据类型")
    description = models.CharField(max_length=50, blank=True, verbose_name=u"描述")
    createdBy = models.ForeignKey('BP', related_name='creator', verbose_name=u"创建者")
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name=u"创建于")
    updatedBy = models.ForeignKey('BP', related_name='updater', verbose_name=u"更新者")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name=u"更新于")
    priority = models.ForeignKey('PriorityType', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u"优先级")
    status = models.ForeignKey('StatusType', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u"状态")
    deleteFlag = models.BooleanField(default=False, verbose_name=u"删除标记")

    def __unicode__(self):
        return "%s %s %s" % (self.id, self.type.description, self.description)

    def logs(self):
        logText = ''
        for l in self.ordertext_set.order_by('-createdAt'):
            # Build log
            t = '%s %s %s<br>----------<br>%s' % (
                l.type.description, l.createdBy.displayName(), l.createdAt.strftime('%Y-%m-%d %H:%M:%S'), l.content)

            logText = '%s%s<br><br>' % (logText, t)
        return logText

    class Meta:
        verbose_name = u"单据表"
        verbose_name_plural = u"单据表"


# Customized fields for Order
# This table stores extra information for an order based on business needs
# As I said before, regional/specific changes should be limited to XXCustomized table
class OrderCustomized(models.Model):
    order = models.OneToOneField('Order', verbose_name=u"单据")
    travelAmount = models.IntegerField(null=True, blank=True, verbose_name=u"差旅量")
    amount = models.IntegerField(null=True, blank=True, verbose_name=u"额度")
    stage = models.CharField(max_length=5, null=True, blank=True, verbose_name=u"阶段")
    goLiveDate = models.DateField(null=True, blank=True, verbose_name=u"上线日期")
    customerType = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"结算类型")
    tmcExtraFieldsChk = models.BooleanField(default=False)
    connectionVia = models.CharField(max_length=255, null=True, blank=True)
    uploadTimeFreq = models.CharField(max_length=255, null=True, blank=True)
    uatpRatio = models.CharField(max_length=255, null=True, blank=True)
    tmcResEmp = models.CharField(max_length=255, null=True, blank=True)
    settleType = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"账户类型")
    # For extra usage
    file1 = models.FileField(upload_to='attachments', null=True, blank=True, verbose_name=u"附件1")
    file2 = models.FileField(upload_to='attachments', null=True, blank=True, verbose_name=u"附件2")
    imgFile1 = models.ImageField(upload_to='attachments', null=True, blank=True, verbose_name=u"图片1")
    imgFile2 = models.ImageField(upload_to='attachments', null=True, blank=True, verbose_name=u"图片2")
    # Additional status for check
    checkResult = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"审核结果")

    def displayStage(self):
        key = '00003'
        oesft = OrderExtSelectionFieldType.objects.filter(orderType=self.order.type, fieldKey=key, key=self.stage)
        return oesft[0].description

    def __unicode__(self):
        return "%s %s %s %s %s" % (self.order, self.travelAmount, self.amount, self.stage, self.goLiveDate)

    class Meta:
        verbose_name = u"单据扩展表"
        verbose_name_plural = u"单据扩展表"


# Partner function table
# This table stores order and it's related BP
# E.g. A sales order involves customer company, salesman, customer company contacter
# A repair request involves worker, checker
# A development task involves developer(s), tester(s), qa
# That's is to say an order can have multiple bp with different partner function in it
class OrderPF(models.Model):
    order = models.ForeignKey('Order', verbose_name=u"单据")
    pf = models.ForeignKey('PFType', verbose_name=u"关联类型")
    bp = models.ForeignKey('BP', null=True, blank=True, verbose_name=u"关联商业伙伴")
    relatedOrder = models.ForeignKey('Order',
                                     null=True,
                                     blank=True,
                                     related_name="asRelatedOrder",
                                     verbose_name=u"关联单据")
    main = models.BooleanField(default=False, verbose_name=u"主伙伴")

    def __unicode__(self):
        return "%s %s %s" % (self.order, self.pf, self.bp)

    class Meta:
        verbose_name = u"单据商业伙伴关联表"
        verbose_name_plural = u"单据商业伙伴关联表"


# Text table
# This table store text data for an order
# Each order can have multiple texts
class OrderText(models.Model):
    order = models.ForeignKey('Order', verbose_name=u"单据")
    type = models.ForeignKey('TextType', verbose_name=u"文本类型")
    createdBy = models.ForeignKey('BP', related_name='textCreator', verbose_name=u"创建者")
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name=u"创建于")
    content = models.TextField(null=True, blank=True, verbose_name=u"内容")

    def __unicode__(self):
        return "%s %s %s %s %s" % (self.order, self.type, self.createdBy, self.createdAt, self.content)

    class Meta:
        verbose_name = u"单据文本表"
        verbose_name_plural = u"单据文本表"


# This table stores BP texts
class BPText(models.Model):
    bp = models.ForeignKey('BP', verbose_name=u"伙伴")
    type = models.ForeignKey('BPTextType', verbose_name=u"文本类型")
    createdBy = models.ForeignKey('BP', related_name='bpTextCreator', verbose_name=u"创建者")
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name=u"创建于")
    content = models.TextField(null=True, blank=True, verbose_name=u"内容")

    def __unicode__(self):
        return "%s %s %s %s %s" % (self.bp, self.type, self.createdBy, self.createdAt, self.content)

    class Meta:
        verbose_name = u"商业伙伴文本表"
        verbose_name_plural = u"商业伙伴文本表"


# This table defines extra field type(name)
class OrderExtFieldType(models.Model):
    orderType = models.ForeignKey('OrderType', verbose_name=u"单据类型")
    key = models.CharField(max_length=5, verbose_name=u"主键")
    description = models.CharField(max_length=50, verbose_name=u"描述")

    class Meta:
        db_table = 'sales_OrderExtFieldType'
        unique_together = ("orderType", "key")
        verbose_name = u"单据扩展字段类型表"
        verbose_name_plural = u"单据扩展字段类型表"

    def __unicode__(self):
        return "%s(%s)" % (self.key, self.description)


# This table defines extra field
# But it need redesign, and seems not used now
class OrderExtField(models.Model):
    type = models.ForeignKey('OrderExtFieldType', verbose_name=u"扩展字段类型")
    originalOrder = models.ForeignKey('Order', verbose_name=u"单据")
    value = models.CharField(max_length=50, null=True, blank=True, verbose_name=u"值")
    relatedBp = models.ForeignKey('BP', null=True, blank=True, verbose_name=u"关联伙伴")
    relatedOrder = models.ForeignKey('Order', related_name='relatedOrder_set', null=True, blank=True,
                                     verbose_name=u"关联单据")
    relatedSelection = models.ForeignKey('OrderExtSelectionFieldType', null=True, blank=True, verbose_name=u"关联选项")

    def __unicode__(self):
        return "%s(%s,%s,%s,%s)" % (
            self.type.description, self.value, self.relatedBp, self.relatedOrder, self.relatedSelection)

    class Meta:
        verbose_name = u"单据扩展字段表"
        verbose_name_plural = u"单据扩展字段表"


# This table defines site language, e.g.
# en English
# cn Chinese
class SiteLanguage(models.Model):
    key = models.CharField(max_length=5, verbose_name=u"主键")
    description = models.CharField(max_length=50, verbose_name=u"语言描述")

    def __unicode__(self):
        return "%s(%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"网站语言"
        verbose_name_plural = u"网站语言"


# This table defines site application name for phrase, e.g.
# g_default
# g for global
class SiteAppType(models.Model):
    appId = models.CharField(max_length=20, primary_key=True, verbose_name=u"应用主键")
    description = models.CharField(max_length=50, verbose_name=u"描述")

    def __unicode__(self):
        return "%s(%s)" % (self.appId, self.description)

    class Meta:
        verbose_name = u"网站应用定义表"
        verbose_name_plural = u"网站应用定义表"


# This table defines phrase in site
class SitePhrase(models.Model):
    phraseId = models.CharField(max_length=20, verbose_name=u"短语主键")
    app = models.ForeignKey('SiteAppType', verbose_name=u"应用")
    phraseLan = models.ForeignKey('SiteLanguage', verbose_name=u"语言")
    content = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"内容")
    bigContent = models.TextField(null=True, blank=True, verbose_name=u"大文本内容")

    class Meta:
        db_table = 'sales_SitePhrase'
        unique_together = ("phraseId", "app", "phraseLan")
        verbose_name = u"网站短语国际化表"
        verbose_name_plural = u"网站短语国际化表"

    def __unicode__(self):
        return "%s %s %s %s" % (self.phraseId, self.app.description, self.phraseLan.description, self.content)


# This table defines site menu
# Menu could be different based on role
# Each menu item will trigger an application
# Menu can be customized on air
class SiteMenuItem(models.Model):
    role = models.ForeignKey('UserRoleType', verbose_name=u"用户角色类型")
    parentMenuId = models.ForeignKey('self', null=True, blank=True, verbose_name=u"父菜单编号")
    # Refer to SitePhrase phraseId
    phraseId = models.CharField(max_length=20, null=True, blank=True, verbose_name=u"短语主键")
    appId = models.CharField(max_length=20, null=True, blank=True, verbose_name=u"短语应用")
    pageApp = models.CharField(max_length=50, null=True, blank=True, verbose_name=u"应用")
    sortOrder = models.IntegerField(verbose_name=u"排序号")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")

    def __unicode__(self):
        return "%s %s %s %s" % (self.role.description, self.parentMenuId, self.phraseId, self.sortOrder)

    class Meta:
        verbose_name = u"网站菜单定义表"
        verbose_name_plural = u"网站菜单定义表"


# This table defines field type, it determines how field is displayed or edit on page
class FieldType(models.Model):
    key = models.CharField(max_length=2, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")

    def __unicode__(self):
        return "%s(%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"字段类型表"
        verbose_name_plural = u"字段类型表"


# This table defines fields for order
# It describe what field it's, how it should be stored, what phrase is used
class OrderFieldDef(models.Model):
    orderType = models.ForeignKey('OrderType', verbose_name=u"单据类型")
    # The name used in code or html, represent the attribute
    fieldKey = models.CharField(max_length=50, verbose_name=u"字段主键")
    # Type of field:
    # Database - The field is directly store to database table
    # Addition - The field won't be stored
    # Null or blank means Database
    attributeType = models.CharField(max_length=10, null=True, blank=True, verbose_name=u"字段属性")
    # Field type, input, selection etc
    fieldType = models.ForeignKey('FieldType', verbose_name=u"字段类型")
    # Used to descibe data type stored
    # Available value:
    # Number
    # Date
    # String
    # Boolean
    valueType = models.CharField(max_length=10, null=True, blank=True, verbose_name=u"值类型")
    # Which table to store, PF, Text etc
    storeType = models.CharField(max_length=50, null=True, blank=True, verbose_name=u"存储类型")
    # Column name in related table
    storeColumn = models.CharField(max_length=50, null=True, blank=True, verbose_name=u"存储字段")
    # Key related to storeType
    # e.g for storeType PF, key is defined in PFTypes
    # for storeType Customized, storeColumn is the column name in OrderCustomized table
    storeKey = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"存储键值")

    def __unicode__(self):
        return "%s %s %s %s %s %s %s" % (
            self.orderType, self.fieldKey, self.fieldType, self.valueType, self.storeType, self.storeColumn,
            self.storeKey)

    class Meta:
        verbose_name = u"单据字段定义表"
        verbose_name_plural = u"单据字段定义表"


# This table defines BP fields, similar as OrderFieldDef
class BPFieldDef(models.Model):
    bpType = models.ForeignKey('BPType', verbose_name=u"伙伴类型")
    # The name used in code or html, represent the attribute
    fieldKey = models.CharField(max_length=50, verbose_name=u"字段主键")
    # Type of field:
    # Database - The field is directly store to database table
    # Addition - The field won't be stored
    # Null or blank means Database
    attributeType = models.CharField(max_length=10, null=True, blank=True, verbose_name=u"字段属性")
    # Field type, input, selection etc
    fieldType = models.ForeignKey('FieldType', verbose_name=u"字段类型")
    # Used to descibe data type stored
    # Available value:
    # Number
    # Date
    # String
    # Boolean
    valueType = models.CharField(max_length=10, null=True, blank=True, verbose_name=u"值类型")
    # Which table to store, PF, Text etc
    storeType = models.CharField(max_length=50, null=True, blank=True, verbose_name=u"存储类型")
    # Column name in related table
    storeColumn = models.CharField(max_length=50, null=True, blank=True, verbose_name=u"存储字段")
    # Key related to storeType
    # e.g for storeType PF, key is defined in PFTypes
    # for storeType Customized, storeColumn is the column name in OrderCustomized table
    storeKey = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"存储键值")

    def __unicode__(self):
        return "%s %s %s %s %s %s %s" % (
            self.bpType, self.fieldKey, self.fieldType, self.valueType, self.storeType, self.storeColumn,
            self.storeKey)

    class Meta:
        verbose_name = u"商业伙伴字段定义表"
        verbose_name_plural = u"商业伙伴字段定义表"


# This table stores user search criteria
class UserSavedSearchFavorite(models.Model):
    userlogin = models.ForeignKey('UserLogin', verbose_name=u"用户登录信息")
    # Order type or other value, e.g 'commonOrder'
    type = models.CharField(max_length=255, verbose_name=u"类型")
    # User saved name
    name = models.CharField(max_length=255, verbose_name=u"存储名称")
    sortOrder = models.IntegerField(verbose_name=u"排序号")
    property = models.CharField(max_length=255, verbose_name=u"字段")
    operation = models.CharField(max_length=255, verbose_name=u"操作符")
    low = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"低端值")
    high = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"高端值")

    def __unicode__(self):
        return "%s %s %s [%s %s %s %s]" % (
            self.userlogin, self.type, self.name, self.property, self.operation, self.low, self.high)

    class Meta:
        verbose_name = u"用户搜索字段保存表"
        verbose_name_plural = u"用户搜索字段保存表"


# This table defines business entity class name which is used in python code
# This means you can create different entity class to handle different order
class OrderBEDef(models.Model):
    orderType = models.ForeignKey('OrderType', verbose_name=u"单据类型")
    businessEntity = models.CharField(max_length=20, verbose_name=u"单据业务实体")

    def __unicode__(self):
        return "%s %s" % (self.orderType, self.businessEntity)

    class Meta:
        verbose_name = u"单据实体定义表"
        verbose_name_plural = u"单据实体定义表"


# This table defines business partner entity, similar as OrderBEDef
class BPBEDef(models.Model):
    bpType = models.ForeignKey('BPType', verbose_name=u"伙伴类型")
    businessEntity = models.CharField(max_length=20, verbose_name=u"伙伴业务实体")

    def __unicode__(self):
        return "%s %s" % (self.bpType, self.businessEntity)

    class Meta:
        verbose_name = u"商业伙伴实体定义表"
        verbose_name_plural = u"商业伙伴实体定义表"


# This table defines view type
# Currently only 3: Search, Detail, Result
class ViewType(models.Model):
    key = models.CharField(max_length=10, primary_key=True, verbose_name=u"主键")
    description = models.CharField(max_length=255, verbose_name=u"描述")

    def __unicode__(self):
        return "%s (%s)" % (self.key, self.description)

    class Meta:
        verbose_name = u"视图类型定义表"
        verbose_name_plural = u"视图类型定义表"


# This table stores configuration of how order fields is display on screen
# I don't like hardcode, even for html view
class StdViewLayoutConf(models.Model):
    field = models.ForeignKey('OrderFieldDef', verbose_name=u"字段定义")
    businessRole = models.ForeignKey('UserRoleType', null=True, blank=True, verbose_name=u"业务角色")
    viewType = models.ForeignKey('ViewType', verbose_name=u"视图类型")
    visibility = models.BooleanField(verbose_name=u"是否可见")
    required = models.BooleanField(default=False, verbose_name=u"是否必须")
    editable = models.BooleanField(default=True, verbose_name=u"可否编辑")
    labelPhraseId = models.CharField(max_length=20, verbose_name=u"标签短语主键")
    appId = models.CharField(max_length=20, verbose_name=u"短语应用主键")
    locRow = models.IntegerField(verbose_name=u"所在行")
    locCol = models.IntegerField(verbose_name=u"所在列")
    locWidth = models.CharField(max_length=20, null=True, blank=True, verbose_name=u"宽度")
    locHeight = models.CharField(max_length=20, null=True, blank=True, verbose_name=u"高度")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")

    class Meta:
        verbose_name = u"单据标准视图配置表"
        verbose_name_plural = u"单据标准视图配置表"


# This table stores configuration of how BP fields is displayed on screen
# Why should we hardcode layout on screen?
# Why should not? Because I can
class BPStdViewLayoutConf(models.Model):
    field = models.ForeignKey('BPFieldDef', verbose_name=u"字段定义")
    businessRole = models.ForeignKey('UserRoleType', null=True, blank=True, verbose_name=u"业务角色")
    viewType = models.ForeignKey('ViewType', verbose_name=u"视图类型")
    visibility = models.BooleanField(verbose_name=u"是否可见")
    required = models.BooleanField(default=False, verbose_name=u"是否必须")
    editable = models.BooleanField(default=True, verbose_name=u"可否编辑")
    labelPhraseId = models.CharField(max_length=20, verbose_name=u"标签短语主键")
    appId = models.CharField(max_length=20, verbose_name=u"短语应用主键")
    locRow = models.IntegerField(verbose_name=u"所在行")
    locCol = models.IntegerField(verbose_name=u"所在列")
    locWidth = models.CharField(max_length=20, null=True, blank=True, verbose_name=u"宽度")
    locHeight = models.CharField(max_length=20, null=True, blank=True, verbose_name=u"高度")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")

    class Meta:
        verbose_name = u"商业伙伴标准视图配置表"
        verbose_name_plural = u"商业伙伴标准视图配置表"


# This table is no longer needed
# Todo remove this table later
class UserOrderViewHistory(models.Model):
    userlogin = models.ForeignKey('UserLogin', verbose_name=u"用户登录信息")
    orderId = models.IntegerField(verbose_name=u"单据编号")
    viewedAt = models.DateTimeField(auto_now=True, verbose_name=u"查看时间")

    class Meta:
        verbose_name = u"用户单据查看历史记录表（废除）"
        verbose_name_plural = u"用户单据查看历史记录表（废除）"


# This table stores user view history, no matter order or bp records
class UserViewHistory(models.Model):
    userlogin = models.ForeignKey('UserLogin', verbose_name=u"用户登录信息")
    objectId = models.IntegerField(verbose_name=u"实体编号")
    # Type 'Order', 'BP'
    type = models.CharField(max_length=20, verbose_name=u"类型")
    viewedAt = models.DateTimeField(auto_now=False, verbose_name=u"查看时间")

    class Meta:
        verbose_name = u"用户单据查看历史记录表"
        verbose_name_plural = u"用户单据查看历史记录表"


# This table is no longer used
class OrderHistory(models.Model):
    orderId = models.IntegerField(verbose_name=u"单据编号")
    orderField = models.CharField(max_length=50, verbose_name=u"单据字段")
    oldValue = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"字段旧值")
    oldKeyValue = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"字段旧键值")
    newValue = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"字段新值")
    newKeyValue = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"字段新键值")
    # UpdatedBy should be a BP, here store the id, but not required as Foreign key
    updatedBy = models.CharField(max_length=255, verbose_name=u"更新者")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name=u"更新于")

    class Meta:
        verbose_name = u"单据历史记录表（废除）"
        verbose_name_plural = u"单据历史记录表（废除）"


# This table stores order change history
# To record user operation is necessary, a system should allow you to track
# what did user do, otherwise it's bad
class ChangeHistory(models.Model):
    objectId = models.IntegerField(verbose_name=u"实体编号")
    # 'Order', 'BP'
    type = models.CharField(max_length=50, verbose_name=u"实体类型")
    objectField = models.CharField(max_length=50, verbose_name=u"实体字段")
    oldValue = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"字段旧值")
    oldKeyValue = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"字段旧键值")
    newValue = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"字段新值")
    newKeyValue = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"字段新键值")
    # UpdatedBy should be a BP, here store the id, but not required as Foreign key
    updatedBy = models.CharField(max_length=255, verbose_name=u"更新者")
    updatedAt = models.DateTimeField(auto_now=False, verbose_name=u"更新于")

    class Meta:
        verbose_name = u"修改历史记录表"
        verbose_name_plural = u"修改历史记录表"


# This table stores lock if user is editing order or bp
class LockTable(models.Model):
    objectId = models.IntegerField(verbose_name=u"实体编号")
    tableType = models.CharField(max_length=50, verbose_name=u"表类型")
    # lockedBy should be a BP, here store the id, but not required as Foreign key
    lockedBy = models.CharField(max_length=255, verbose_name=u"加锁者")
    lockedAt = models.DateTimeField(auto_now=True, verbose_name=u"加锁于")

    class Meta:
        verbose_name = u"实体锁定表"
        verbose_name_plural = u"实体锁定表"


# This table store configuration for whole system
class SystemConfiguration(models.Model):
    key = models.CharField(max_length=50, primary_key=True, verbose_name=u"主键")
    property1 = models.CharField(max_length=50, null=True, blank=True, verbose_name=u"附属键1")
    property2 = models.CharField(max_length=50, null=True, blank=True, verbose_name=u"附属件2")
    value1 = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"值1")
    value2 = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"值2")

    class Meta:
        verbose_name = u"系统配置表"
        verbose_name_plural = u"系统配置表"


# This table stores activity information
# It is similar to ordercustomized, as an extra table for Order
class Activity(models.Model):
    # A one to one reference to order
    order = models.OneToOneField('Order', verbose_name=u"单据")
    startDateTime = models.DateTimeField(null=True, blank=True, verbose_name=u"起始时间")
    endDateTime = models.DateTimeField(null=True, blank=True, verbose_name=u"结束时间")
    visibility = models.CharField(max_length=50, null=True, blank=True, verbose_name=u"可见性")

    class Meta:
        verbose_name = u"活动"
        verbose_name_plural = u"活动"


# This table stores file uploaded, the file is not related to order or bp or anything
# The file uploaded to system is like a share to whole user
class FileAttachment(models.Model):
    name = models.CharField(max_length=50, verbose_name=u"名称")
    description = models.CharField(null=True, blank=True, max_length=255, verbose_name=u"描述")
    version = models.CharField(null=True, blank=True, max_length=50, verbose_name=u"版本")
    actualfilename = models.CharField(null=True, blank=True, max_length=255, verbose_name=u"实际文件名")
    file = models.FileField(upload_to='attachments', verbose_name=u"文件")
    deleteFlag = models.BooleanField(default=False, verbose_name=u"删除标记")

    class Meta:
        verbose_name = u"文件附件"
        verbose_name_plural = u"文件附件"


# This table stores file uploaded related to an order
class OrderFileAttachment(models.Model):
    order = models.ForeignKey('Order', verbose_name=u"单据")
    name = models.CharField(max_length=50, verbose_name=u"名称")
    description = models.CharField(null=True, blank=True, max_length=255, verbose_name=u"描述")
    actualfilename = models.CharField(null=True, blank=True, max_length=255, verbose_name=u"实际文件名")
    file = models.FileField(null=True, blank=True, upload_to='attachments', verbose_name=u"文件")
    image = models.ImageField(null=True, blank=True, upload_to='attachments', verbose_name=u"图片")
    createdBy = models.ForeignKey('BP', related_name='fileCreator', verbose_name=u"创建者")
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name=u"创建于")
    deleteFlag = models.BooleanField(default=False, verbose_name=u"删除标记")

    class Meta:
        verbose_name = u"单据文件附件"
        verbose_name_plural = u"单据文件附件"


# This table stores file uploaded related to BP
# Todo OrderFileAttachment and BPFileAttachment can be merge into one table
class BPFileAttachment(models.Model):
    bp = models.ForeignKey('BP', verbose_name=u"商业伙伴")
    name = models.CharField(max_length=50, verbose_name=u"名称")
    description = models.CharField(null=True, blank=True, max_length=255, verbose_name=u"描述")
    actualfilename = models.CharField(null=True, blank=True, max_length=255, verbose_name=u"实际文件名")
    file = models.FileField(null=True, blank=True, upload_to='bpAttachments', verbose_name=u"文件")
    image = models.ImageField(null=True, blank=True, upload_to='bpAttachments', verbose_name=u"图片")
    createdBy = models.ForeignKey('BP', related_name='bpFileCreator', verbose_name=u"创建者")
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name=u"创建于")
    deleteFlag = models.BooleanField(default=False, verbose_name=u"删除标记")

    class Meta:
        verbose_name = u"商业伙伴文件附件"
        verbose_name_plural = u"商业伙伴文件附件"


# This table stores file user uploaded but relationship will be saved only when user
# saved order or bp(file be removed from this table and saved to OrderFileAttachment
# or BPFileAttachment), file in this table and folder uploads can be removed at anytime.
class UploadFilesTemp(models.Model):
    imageFile = models.ImageField(upload_to='uploads', verbose_name=u"图片文件")
    normalFile = models.FileField(upload_to='uploads', verbose_name=u"普通文件")

    class Meta:
        verbose_name = u"临时上传文件"
        verbose_name_plural = u"临时上传文件"


# This table stores bp mapping between this system and outside system
class SLTAccountMapping(models.Model):
    bpId = models.IntegerField(verbose_name=u"CRM企业（BP）Id")
    sltAccountNumber = models.CharField(max_length=255, null=False, blank=False, verbose_name=u"山旅通账户（Account Number）")
    accountMemo = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"账户备注")
    agentBpId = models.IntegerField(null=True, blank=True, verbose_name=u"CRM代理商（BP）Id")
    sltAgentId = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"TMC账户（Agent Id）")
    agentMemo = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"TMC备注")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")

    class Meta:
        verbose_name = u"山旅通账户关联表"
        verbose_name_plural = u"山旅通账户关联表"


class OrderFollowUpDef(models.Model):
    orderTypeA = models.ForeignKey('OrderType', related_name="asFollowUpTypeA", verbose_name=u"单据类型A")
    orderTypeB = models.ForeignKey('OrderType', related_name="asFollowUpTypeB", verbose_name=u"单据类型B")
    relation = models.ForeignKey('OrderRelType', verbose_name=u"关系类型")
    comments = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"备注")
    valid = models.BooleanField(default=True, verbose_name=u"有效性")

    class Meta:
        verbose_name = u"单据跟进类型定义表"
        verbose_name_plural = u"单据跟进类型定义表"


# This table is for user access log, let's see how many PV I have
class AppNavAccess(models.Model):
    userLogin = models.ForeignKey('UserLogin', verbose_name=u"用户登录信息")
    type = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"类型")
    pageApp = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"应用")
    pageAction = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"动作")
    pageParams = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"参数")
    pageMode = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"模式")
    accessedAt = models.DateTimeField(auto_now=True, verbose_name=u"更新于")

    class Meta:
        verbose_name = u"应用访问日志"
        verbose_name_plural = u"应用访问日志"


# This table is for user feedbacks
class UserFeedback(models.Model):
    userLogin = models.ForeignKey('UserLogin', verbose_name=u"用户登录信息")
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=u"标题")
    type = models.CharField(max_length=50, null=True, blank=True, verbose_name=u"类型")
    text = models.TextField(null=True, blank=True, verbose_name=u"内容")

    class Meta:
        verbose_name = u"用户反馈"
        verbose_name_plural = u"用户反馈"


# This table is for messaging between user
class SiteMessage(models.Model):
    sender = models.ForeignKey('UserLogin', related_name="asMessageSender", verbose_name=u"发送者")
    receiver = models.ForeignKey('UserLogin', related_name="asMessageReceiver", verbose_name=u"接收者")
    message = models.TextField(null=True, blank=True, verbose_name=u"内容")
    sentAt = models.DateTimeField(verbose_name=u"发送时间")
    receiverReadFlag = models.BooleanField(default=False, verbose_name=u"接收者已读标记")
    receiverDeleteFlag = models.BooleanField(default=False, verbose_name=u"接收者删除标记")
    senderDeleteFlag = models.BooleanField(default=False, verbose_name=u"发送者删除标记")

    class Meta:
        verbose_name = u"用户消息表"
        verbose_name_plural = u"用户消息表"
