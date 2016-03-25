from django.contrib import admin

# -*- coding: UTF-8 -*-
from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('nickName', 'realName')


admin.site.register(User, UserAdmin)


class UserLoginStatusAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


admin.site.register(UserLoginStatus, UserLoginStatusAdmin)


class UserLoginAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'user', 'userbp', 'password', 'passwordEncrypted', 'status', 'failureCount', 'lastLoginAt',
        'pulseAt')


admin.site.register(UserLogin, UserLoginAdmin)


class AuthObjectAdmin(admin.ModelAdmin):
    list_display = ('authObject', 'create', 'read', 'update', 'delete')


admin.site.register(AuthObject, AuthObjectAdmin)


class AuthObjectTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


admin.site.register(AuthObjectType, AuthObjectTypeAdmin)


class UserRoleTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


admin.site.register(UserRoleType, UserRoleTypeAdmin)


class UserProfileTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


admin.site.register(UserProfileType, UserProfileTypeAdmin)


class BPAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'type', 'partnerNo', 'firstName', 'middleName', 'lastName', 'name1', 'name2', 'name3', 'name4', 'title',
        'mobile', 'email', 'valid',
        'deleteFlag')
    search_fields = (
    'partnerNo', 'firstName', 'middleName', 'lastName', 'name1', 'name2', 'name3', 'name4', 'title', 'mobile', 'email')


admin.site.register(BP, BPAdmin)


class BPBaseTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


class BPTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'baseType', 'description', 'assignmentBlock')


admin.site.register(BPType, BPTypeAdmin)


class BPRelTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'description', 'descAtoB', 'descBtoA')


admin.site.register(BPRelType, BPRelTypeAdmin)


class BPRelationAdmin(admin.ModelAdmin):
    list_display = ('bpA', 'relation', 'bpB', 'comments', 'valid')


admin.site.register(BPRelation, BPRelationAdmin)


class BPCustomizedAdmin(admin.ModelAdmin):
    list_display = (
        'bp', 'boolAttribute1', 'boolAttribute2', 'boolAttribute3', 'empResp', 'legalPerson', 'actualPerson',
        'corpStructure', 'corpLiscense', 'file1', 'file2', 'imgFile1', 'imgFile2')


admin.site.register(BPCustomized, BPCustomizedAdmin)


class AddressTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


admin.site.register(AddressType, AddressTypeAdmin)


class DistrictTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


admin.site.register(DistrictType, DistrictTypeAdmin)


class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'type', 'district', 'address1', 'address2', 'address3', 'address4', 'phone1', 'contact1', 'phone2', 'contact2')


admin.site.register(Address, AddressAdmin)


class OrderTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'baseType', 'description', 'assignmentBlock')


admin.site.register(OrderType, OrderTypeAdmin)


class OrderBaseTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


admin.site.register(OrderBaseType, OrderBaseTypeAdmin)


class OrderRelTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'description', 'descAtoB', 'descBtoA')


admin.site.register(OrderRelType, OrderRelTypeAdmin)


class OrderRelationAdmin(admin.ModelAdmin):
    list_display = ('orderA', 'relation', 'orderB', 'comments', 'valid')


admin.site.register(OrderRelation, OrderRelationAdmin)


class PFTypeAdmin(admin.ModelAdmin):
    list_display = ('orderType', 'key', 'description')


admin.site.register(PFType, PFTypeAdmin)


class PriorityTypeAdmin(admin.ModelAdmin):
    list_display = ('orderType', 'key', 'description', 'sortOrder')


admin.site.register(PriorityType, PriorityTypeAdmin)


class StatusTypeAdmin(admin.ModelAdmin):
    list_display = ('orderType', 'key', 'description', 'sortOrder')


admin.site.register(StatusType, StatusTypeAdmin)


class OrderExtSelectionFieldTypeAdmin(admin.ModelAdmin):
    list_display = ('orderType', 'fieldKey', 'key', 'description', 'sortOrder')


admin.site.register(OrderExtSelectionFieldType, OrderExtSelectionFieldTypeAdmin)


class TextTypeAdmin(admin.ModelAdmin):
    list_display = ('orderType', 'key', 'description')


admin.site.register(TextType, TextTypeAdmin)


class BPTextTypeAdmin(admin.ModelAdmin):
    list_display = ('bpType', 'key', 'description')


admin.site.register(BPTextType, BPTextTypeAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'type', 'description', 'createdBy', 'createdAt', 'updatedBy', 'updatedAt', 'priority', 'status',
        'deleteFlag')
    search_fields = ('id', 'description')


admin.site.register(Order, OrderAdmin)


class OrderCustomizedAdmin(admin.ModelAdmin):
    list_display = ('order', 'travelAmount', 'amount', 'stage', 'goLiveDate', 'file1', 'file2', 'imgFile1', 'imgFile2')


admin.site.register(OrderCustomized, OrderCustomizedAdmin)


class OrderPFAdmin(admin.ModelAdmin):
    list_display = ('order', 'pf', 'bp', 'relatedOrder', 'main')


admin.site.register(OrderPF, OrderPFAdmin)


class OrderTextAdmin(admin.ModelAdmin):
    list_display = ('type', 'order', 'createdBy', 'createdAt', 'content')
    search_fields = ('content',)


admin.site.register(OrderText, OrderTextAdmin)


class BPTextAdmin(admin.ModelAdmin):
    list_display = ('type', 'bp', 'createdBy', 'createdAt', 'content')
    search_fields = ('content',)


admin.site.register(BPText, BPTextAdmin)


class OrderExtFieldTypeAdmin(admin.ModelAdmin):
    list_display = ('orderType', 'key', 'description')


admin.site.register(OrderExtFieldType, OrderExtFieldTypeAdmin)


class OrderExtFieldAdmin(admin.ModelAdmin):
    list_display = ('type', 'originalOrder', 'value', 'relatedBp', 'relatedOrder', 'relatedSelection')


admin.site.register(OrderExtField, OrderExtFieldAdmin)


class SiteLanguageAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


admin.site.register(SiteLanguage, SiteLanguageAdmin)


class SiteAppTypeAdmin(admin.ModelAdmin):
    list_display = ('appId', 'description')


admin.site.register(SiteAppType, SiteAppTypeAdmin)


class SitePhraseAdmin(admin.ModelAdmin):
    list_display = ('phraseId', 'app', 'phraseLan', 'content', 'bigContent')
    search_fields = ('phraseId', 'content', 'bigContent')


admin.site.register(SitePhrase, SitePhraseAdmin)


class SiteMenuItemAdmin(admin.ModelAdmin):
    list_display = ('role', 'parentMenuId', 'phraseId', 'appId', 'pageApp', 'sortOrder', 'valid')


admin.site.register(SiteMenuItem, SiteMenuItemAdmin)


class FieldTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


admin.site.register(FieldType, FieldTypeAdmin)


class OrderFieldDefAdmin(admin.ModelAdmin):
    list_display = (
        'orderType', 'fieldKey', 'attributeType', 'fieldType', 'valueType', 'storeType', 'storeColumn', 'storeKey')


admin.site.register(OrderFieldDef, OrderFieldDefAdmin)


class BPFieldDefAdmin(admin.ModelAdmin):
    list_display = (
        'bpType', 'fieldKey', 'attributeType', 'fieldType', 'valueType', 'storeType', 'storeColumn', 'storeKey')


admin.site.register(BPFieldDef, BPFieldDefAdmin)


class UserSavedSearchFavoriteAdmin(admin.ModelAdmin):
    list_display = ('userlogin', 'type', 'name', 'sortOrder', 'property', 'operation', 'low', 'high')


admin.site.register(UserSavedSearchFavorite, UserSavedSearchFavoriteAdmin)


class OrderBEDefAdmin(admin.ModelAdmin):
    list_display = ('orderType', 'businessEntity')


admin.site.register(OrderBEDef, OrderBEDefAdmin)


class BPBEDefAdmin(admin.ModelAdmin):
    list_display = ('bpType', 'businessEntity')


admin.site.register(BPBEDef, BPBEDefAdmin)


class ViewTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


admin.site.register(ViewType, ViewTypeAdmin)


class StdViewLayoutConfAdmin(admin.ModelAdmin):
    list_display = (
        'field', 'businessRole', 'viewType', 'locRow', 'locCol', 'locWidth', 'locHeight', 'visibility', 'required',
        'labelPhraseId', 'appId', 'valid')


admin.site.register(StdViewLayoutConf, StdViewLayoutConfAdmin)


class BPStdViewLayoutConfAdmin(admin.ModelAdmin):
    list_display = (
        'field', 'businessRole', 'viewType', 'locRow', 'locCol', 'locWidth', 'locHeight', 'visibility', 'required',
        'labelPhraseId', 'appId', 'valid')


admin.site.register(BPStdViewLayoutConf, BPStdViewLayoutConfAdmin)


class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('userlogin', 'role', 'valid')


admin.site.register(UserRole, UserRoleAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('userlogin', 'profile', 'valid')


admin.site.register(UserProfile, UserProfileAdmin)


class UserParameterAdmin(admin.ModelAdmin):
    list_display = ('userlogin', 'name', 'value')


admin.site.register(UserParameter, UserParameterAdmin)


class UserSingleAuthObjectsAdmin(admin.ModelAdmin):
    list_display = ('userlogin', 'singleAuthObject', 'valid')


admin.site.register(UserSingleAuthObject, UserSingleAuthObjectsAdmin)


class UserProfileAuthObjectAdmin(admin.ModelAdmin):
    list_display = ('profile', 'singleAuthObject', 'valid')


admin.site.register(UserProfileAuthObject, UserProfileAuthObjectAdmin)


class UserViewHistoryAdmin(admin.ModelAdmin):
    list_display = ('userlogin', 'objectId', 'type', 'viewedAt')


admin.site.register(UserViewHistory, UserViewHistoryAdmin)


class ChangeHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'objectId', 'type', 'objectField', 'oldValue', 'oldKeyValue', 'newValue', 'newKeyValue', 'updatedBy',
        'updatedAt')
    search_fields = ('id', 'orderId', 'orderField', 'oldValue', 'oldKeyValue', 'newValue', 'newKeyValue')


admin.site.register(ChangeHistory, ChangeHistoryAdmin)


class LockTableAdmin(admin.ModelAdmin):
    list_display = ('objectId', 'tableType', 'lockedBy', 'lockedAt')


admin.site.register(LockTable, LockTableAdmin)


class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'property1', 'property2', 'value1', 'value2')


admin.site.register(SystemConfiguration, SystemConfigurationAdmin)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('order', 'startDateTime', 'endDateTime', 'visibility')


admin.site.register(Activity, ActivityAdmin)


class FileAttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'version', 'actualfilename', 'file', 'deleteFlag')


admin.site.register(FileAttachment, FileAttachmentAdmin)


class OrderFileAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'name', 'description', 'actualfilename', 'file', 'image', 'createdBy', 'createdAt', 'deleteFlag')


admin.site.register(OrderFileAttachment, OrderFileAttachmentAdmin)


class BPFileAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'bp', 'name', 'description', 'actualfilename', 'file', 'image', 'createdBy', 'createdAt', 'deleteFlag')


admin.site.register(BPFileAttachment, BPFileAttachmentAdmin)


class UploadFilesTempAdmin(admin.ModelAdmin):
    list_display = ('imageFile', 'normalFile')


admin.site.register(UploadFilesTemp, UploadFilesTempAdmin)


class SLTAccountMappingAdmin(admin.ModelAdmin):
    search_fields = ('id', 'bpId', 'sltAccountNumber', 'accountMemo', 'agentBpId', 'sltAgentId', 'agentMemo')
    list_display = ('id', 'bpId', 'sltAccountNumber', 'accountMemo', 'agentBpId', 'sltAgentId', 'agentMemo')


admin.site.register(SLTAccountMapping, SLTAccountMappingAdmin)


class OrderFollowUpDefAdmin(admin.ModelAdmin):
    list_display = ('orderTypeA', 'relation', 'orderTypeB', 'comments', 'valid')


admin.site.register(OrderFollowUpDef, OrderFollowUpDefAdmin)


class AppNavAccessAdmin(admin.ModelAdmin):
    list_display = ('userLogin', 'type', 'pageApp', 'pageAction', 'pageParams', 'pageMode', 'accessedAt')


admin.site.register(AppNavAccess, AppNavAccessAdmin)


class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('userLogin', 'title', 'type', 'text')


admin.site.register(UserFeedback, UserFeedbackAdmin)


class SiteMessageAdmin(admin.ModelAdmin):
    list_display = (
        'sender', 'receiver', 'message', 'sentAt', 'receiverReadFlag', 'receiverDeleteFlag', 'senderDeleteFlag')


admin.site.register(SiteMessage, SiteMessageAdmin)
