# -*- coding: UTF-8 -*-
from django import template
from crm.common import *

register = template.Library()


class UtilTag(template.Node):
    def __init__(self, name):
        self.name = name.strip('"')

    def buildViewHistory(self, context):
        uid = context['request'].session['up']['userloginid']
        userLogin = UserLogin.objects.get(id=uid)
        liResult = ''
        allViewHistory = UserViewHistory.objects.filter(userlogin=userLogin).order_by('-viewedAt')
        for history in allViewHistory:
            if history.type == 'Order':
                order = Order.objects.filter(deleteFlag=False, id=history.objectId)
                if not order:
                    continue
                order = order[0]
                li = ''.join(
                    ["""<li class="list-group-item">""", """<a href="#" onclick="toNav('commonOrder','view','""",
                     str(order.id),
                     """','nosearch')">""", order.description, "</a></li>"])
                liResult = ''.join([liResult, li])
            elif history.type == 'BP':
                bp = BP.objects.filter(deleteFlag=False, id=history.objectId)
                if not bp:
                    continue
                bp = bp[0]
                li = ''.join(
                    ["""<li class="list-group-item">""", """<a href="#" onclick="toNav('commonBp','view','""",
                     str(bp.id),
                     """','nosearch')">""", bp.displayName(), "</a></li>"])
                liResult = ''.join([liResult, li])
        html = ''.join(["""<ul class="list-group">""", liResult, "</ul>"])
        html = """<div class="alert-info">
        <div class="panel-heading">
          <h3 class="panel-title">%s</h3>
        </div>
          %s
        </div>""" % (getPhrase(context['request'], 'g_default', 'recentOrder'), html)
        return html

    def buildToolbar(self, context, type):
        canEdit = False
        if type == 'Order':
            appName = 'commonOrder'
            vContext = getContext(context['request'], coCtxName)
            if vContext.orderType:
                # Check whether user has access to edit this kind of order
                authName = 'Order_%s_Access' % vContext.orderType
                (_, _, canEdit, _) = getUserAuthorization(context, authName)
        elif type == 'BP':
            appName = 'commonBp'
            vContext = getContext(context['request'], cbCtxName)
            if vContext.bpType:
                # Check whether user has access to edit this kind of bp
                authName = 'BP_%s_Access' % vContext.bpType
                (_, _, canEdit, _) = getUserAuthorization(context, authName)
        else:
            appName = ''
        pageStatus = context['nav']['pageStatus']
        showBack = True
        if pageStatus == "detail":
            backBtn = """
    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','back')">%(phrase)s</button>
    """ % {'appName': appName, 'phrase': getPhrase(context['request'], 'g_default', 'back')}
            editBtn = ''
            if canEdit:
                editBtn = """
        <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','edit','1')">%(phrase)s</button>
        """ % {'appName': appName, 'phrase': getPhrase(context['request'], 'g_default', 'edit')}
            if showBack:
                buttons = ''.join([backBtn, editBtn])
            else:
                buttons = editBtn
        elif pageStatus == "new":
            backBtn = """
    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','back')">%(phrase)s</button>
    """ % {'appName': appName, 'phrase': getPhrase(context['request'], 'g_default', 'back')}
            saveBtn = """
    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','save')">%(phrase)s</button>
    """ % {'appName': appName, 'phrase': getPhrase(context['request'], 'g_default', 'save')}
            cancelBtn = """
    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','cancel')">%(phrase)s</button>
    """ % {'appName': appName, 'phrase': getPhrase(context['request'], 'g_default', 'cancel')}
            if showBack:
                buttons = ''.join([backBtn, saveBtn, cancelBtn])
            else:
                buttons = ''.join([saveBtn, cancelBtn])
        elif pageStatus == 'edit':
            backBtn = """
    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','back')">%(phrase)s</button>
    """ % {'appName': appName, 'phrase': getPhrase(context['request'], 'g_default', 'back')}
            saveBtn = """
    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','save')">%(phrase)s</button>
    """ % {'appName': appName, 'phrase': getPhrase(context['request'], 'g_default', 'save')}
            cancelBtn = """
    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','cancel')">%(phrase)s</button>
    """ % {'appName': appName, 'phrase': getPhrase(context['request'], 'g_default', 'cancel')}
            followUpBtn = ''
            followUpTypeList = []
            if type == 'Order':
                # Find all possible follow up order type by current order type
                followUpTypeList = [t.orderTypeB for t in
                                    OrderFollowUpDef.objects.filter(orderTypeA__key=vContext.orderType, valid=True)]
            if followUpTypeList:
                # Build follow up button
                itemList = ''
                for followUpType in followUpTypeList:
                    item = """<li><a data-value="classic" href="%(javascript)s"> %(phrase)s</a></li>""" % {
                        'javascript': "javascript:toNavWith('f','commonOrder','createFollowUp','%s','%s')" % (
                            vContext.orderId, followUpType.key),
                        'phrase': followUpType.description
                    }
                    itemList = ''.join([itemList, item])
                followUpBtn = """
<div class="btn-group">
  <button class="btn btn-primary btn-sm dropdown-toggle" data-toggle="dropdown">
    <span class="hidden-sm hidden-xs"> %(phrase)s</span>
    <span class="caret"></span>
  </button>
  <ul class="dropdown-menu">
    %(itemList)s
  </ul>
</div>""" % {'phrase': getPhrase(context['request'], 'g_default', 'createFollowUp'),
             'itemList': itemList}
            buttons = ''.join([saveBtn, cancelBtn, followUpBtn])
        elif pageStatus == 'search':

            buttons = """
    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','search')">%(phrase)s</button>""" % {
                'appName': appName, 'phrase': getPhrase(context['request'], 'g_default', 'search')}
            buttons += """
    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','search','crcls')">%(phrase)s</button>""" % {
                'appName': appName, 'phrase': getPhrase(context['request'], 'g_default', 'clear')}
            buttons += """
    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','search','cradd')"> + </button>""" % {
                'appName': appName}
            if len(vContext.searchBean.getList()) > 3:
                removeFieldButton = """
    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','search','crrmv')"> - </button>""" % {
                    'appName': appName}
                buttons = ''.join([buttons, removeFieldButton])
            saveSearchDiv = """&nbsp;%(phrase1)s <input type="text" class="" name="saveAs" placeholder="" value="">
                    <button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%(appName)s','search','crsav')">%(phrase2)s</button>
                    """ % {'appName': appName, 'phrase1': getPhrase(context['request'], 'g_default', 'saveAs'),
                           'phrase2': getPhrase(context['request'], 'g_default', 'save')}
            buttons = ''.join([buttons, saveSearchDiv])
        html = ''.join(["""{% load PhraseTag %}
            <div class="row">
              <div class="col-md-6">
              """, buttons, """
              </div>
            </div>""", html_separator])
        t = Template(html)
        html = t.render(context)
        return html

    def buildResultToolbar(self, context, type):
        typeList = []
        if type == 'Order':
            appName = 'commonOrder'
            createPhrase = 'createOrder'
            createTxtPhrase = 'createOrderTxt'
            vContext = getContext(context['request'], coCtxName)
            # Check user authorization for order type he can create
            for ot in OrderType.objects.all():
                typeItem = {}
                authName = 'Order_%s_Access' % ot.key
                (canCreate, _, _, _) = getUserAuthorization(context, authName)
                if canCreate:
                    typeItem['key'] = ot.key
                    typeItem['description'] = ot.description
                    typeList.append(typeItem)
        elif type == 'BP':
            appName = 'commonBp'
            createPhrase = 'createBp'
            createTxtPhrase = 'createBpTxt'
            vContext = getContext(context['request'], cbCtxName)
            # Check user authorization for bp type he can create
            for bt in BPType.objects.filter(~Q(key='ZZ')):
                typeItem = {}
                authName = 'BP_%s_Access' % bt.key
                (canCreate, _, _, _) = getUserAuthorization(context, authName)
                if canCreate:
                    typeItem['key'] = bt.key
                    typeItem['description'] = bt.description
                    typeList.append(typeItem)
        else:
            appName = ''
        if len(typeList) != 0:
            # If user can at least create one type of order or bp, display new button
            buttons = """{% load PhraseTag %}<button class="btn btn-primary btn-sm" data-toggle="modal" data-target="#entityTypeModal"> {% PhraseTag g_default new %}</button>"""
            entityTypeModalTemplate = """
                <div class="modal fade" id="entityTypeModal" tabindex="-1" role="dialog" aria-labelledby="entityModalLabel" aria-hidden="true">
                  <div class="modal-dialog">
                    <div class="modal-content">
                      <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal">x</button>
                        <h3>%s</h3>
                      </div>
                      <div class="modal-body">
                        <div class="alert alert-info">
                          %s
                        </div>
                        %s
                      </div>
                      <div class="modal-footer">
                        <button class="btn btn-default" data-dismiss="modal">{%% PhraseTag g_default close %%}</a>
                      </div>
                    </div>
                  </div>
                </div>"""
            entityTypes = [
                """<a href="#" onclick="toNavWith('f','%s','new','%s')" class="list-group-item">%s</a>""" % (appName,
                                                                                                             ot['key'],
                                                                                                             ot[
                                                                                                                 'description'])
                for ot in typeList]
            entityTypesHtml = ''.join(entityTypes)
            entityTypesHtml = ''.join(['<div class="list-group">', entityTypesHtml, '</div>'])
            entityTypeModalHtml = entityTypeModalTemplate % (
                getPhrase(context['request'], 'g_default', createPhrase),
                getPhrase(context['request'], 'g_default', createTxtPhrase),
                entityTypesHtml)
            buttons = ''.join([buttons, entityTypeModalHtml])
        else:
            buttons = ''
        reids = vContext.reids
        if reids and len(reids) > 0:
            downloadButton = """<button class="btn btn-primary btn-sm" onclick="javascript:toNavWith('f','%s','xlsoutput','','','N')">%s</button>""" % (
                appName, getPhrase(context['request'], 'g_default', 'download'))
            buttons = ''.join([buttons, downloadButton])
        buttons = ''.join([buttons, html_separator])
        t = Template(buttons)
        buttons = t.render(context)
        return buttons

    def buildFields(self, context, entityType):
        if entityType == 'Order':
            ctxName = coCtxName
            phraseAppId = 'order'
            appName = 'commonOrder'
        elif entityType == 'BP':
            ctxName = cbCtxName
            phraseAppId = 'bp'
            appName = 'commonBp'
        else:
            ctxName = ''
            phraseAppId = ''
        # Build fields on detail screen
        # Take Business Entity from session and render fields by definition in orderfieldsdef
        vContext = getContext(context['request'], ctxName)
        pageStatus = vContext.mode
        fieldErrors = vContext.fieldErrors
        if entityType == 'Order':
            be = vContext.currentOrder
            fieldsOfOrder = OrderFieldDef.objects.filter(orderType=vContext.orderType)
            configuredFields = StdViewLayoutConf.objects.filter(field__in=fieldsOfOrder, visibility=True,
                                                                viewType__key='Detail', valid=True).order_by('locRow',
                                                                                                             'locCol')
        elif entityType == 'BP':
            be = vContext.currentBp
            fieldsOfBP = BPFieldDef.objects.filter(bpType=vContext.bpType)
            configuredFields = BPStdViewLayoutConf.objects.filter(field__in=fieldsOfBP, visibility=True,
                                                                  viewType__key='Detail', valid=True).order_by('locRow',
                                                                                                               'locCol')
        # Set the pageStatus to entity so that user can customize based on status
        be.pageStatus = pageStatus
        html = '{% load PhraseTag %}'
        row = 0
        for cf in configuredFields:
            if cf.locRow != int(row):
                if row == 0:
                    html = ''.join([html, '<div class="row">'])
                else:
                    html = ''.join([html, '</div>', html_separator, '<div class="row">'])
                row += 1
            # Get configuration for each field
            confData = GetFieldConfigData(be, cf)
            phraseAppId = confData['appId']
            # Get field key, field display value, options(if it's selection)
            fieldValue, displayValue, fieldOptions = GetFieldValueAndOptions(be, **confData)
            # If fieldOptions is dictionary, convert to list
            # Selection list looks like [(key,value),(key,value)]
            fieldOptionsList = []
            if type(fieldOptions) == dict:
                for k, v in fieldOptions.items():
                    fieldOptionsList.append((k, v))
            elif type(fieldOptions) == list:
                fieldOptionsList = fieldOptions

            if pageStatus == 'detail':
                # Every field is in readonly mode on detail screen
                confData['editable'] = False
            fieldDivWidth = 'col-md-%s col-xs-%s' % (confData['locWidth'], confData['locWidth'])
            if confData['editable']:
                # Build editable html
                if confData['fieldType'] == 'IN':
                    # Input field
                    error = ''
                    if fieldErrors and fieldErrors.get(confData['fieldKey'], None):
                        error = 'has-error'
                    fieldHtml = """<div class="%s %s"><label for="%s">%s</label><input type="text" class="form-control" name="%s" placeholder="" value="%s"></div>""" % (
                        fieldDivWidth, error, confData['fieldKey'],
                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId']), confData['fieldKey'],
                        fieldValue)
                elif confData['fieldType'] == 'SE':
                    # Selection field
                    error = ''
                    if fieldErrors and fieldErrors.get(confData['fieldKey'], None):
                        error = 'has-error'
                    optionHtml = ''.join([('<option value="%s" %s>%s</option>' % (
                        key, bool(
                            str(key) == str(fieldValue)) and """ selected ="selected" """ or "", desc)) for
                                          key, desc in
                                          fieldOptionsList])
                    if not cf.required:
                        optionHtml = '<option value="">&nbsp;</option>%s' % optionHtml
                    fieldHtml = """<div class="%s %s"><label for="%s">%s</label><select class="form-control" name="%s" data-rel="chosen">%s</select></div>""" % (
                        fieldDivWidth, error, confData['fieldKey'],
                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId']), confData['fieldKey'],
                        optionHtml)
                elif confData['fieldType'] == 'MS':
                    # Selection field
                    error = ''
                    if fieldErrors and fieldErrors.get(confData['fieldKey'], None):
                        error = 'has-error'
                    optionHtml = ''.join([('<option value="%s" %s>%s</option>' % (
                        key, bool(str(key) == str(fieldValue)) and """ selected ="selected" """ or "", desc)) for
                                          key, desc in
                                          fieldOptionsList])
                    if not cf.required:
                        optionHtml = '<option value="">&nbsp;</option>%s' % optionHtml
                    fieldHtml = """<div class="%s %s"><label for="%s">%s</label><select class="form-control" multiple name="%s" data-rel="chosen">%s</select></div>""" % (
                        fieldDivWidth, error, confData['fieldKey'],
                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId']),
                        confData['fieldKey'], optionHtml)
                elif confData['fieldType'] == 'TA':
                    error = ''
                    if fieldErrors and fieldErrors.get(confData['fieldKey'], None):
                        error = 'has-error'
                    fieldHtml = """<div class="%s %s"><label for="%s">%s</label>
                                        <textarea name="%s" class ="well" style="width:100%%">%s</textarea></div>""" % (
                        fieldDivWidth, error, confData['fieldKey'],
                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId']), confData['fieldKey'],
                        fieldValue)
                elif confData['fieldType'] == 'DA':
                    error = ''
                    if fieldErrors and fieldErrors.get(confData['fieldKey'], None):
                        error = 'has-error'
                    fieldHtml = """<div class="%s %s"><label for="%s">%s</label><input type="text" class="form-control" name="%s" id="%s_dp" value="%s"></div>
                                            <script>
                     $(function() {
                        $("#%s_dp").datepicker({ dateFormat: 'yy-mm-dd' });
                      });
                    </script>""" % (
                        fieldDivWidth, error, confData['fieldKey'],
                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId']), confData['fieldKey'],
                        confData['fieldKey'], fieldValue, confData['fieldKey'])
                elif confData['fieldType'] == 'DT':
                    error = ''
                    if fieldErrors and fieldErrors.get(confData['fieldKey'], None):
                        error = 'has-error'
                    fieldHtml = """<div class="%s %s"><label for="%s">%s</label><input type="text" class="form-control" name="%s" id="%s_dtp" value="%s"></div>
                                                <script>
                         $(function() {
                            $("#%s_dtp").datetimepicker({ dateFormat: 'yy-mm-dd hh:ii',startView:1});
                          });
                        </script>""" % (fieldDivWidth, error, confData['fieldKey'],
                                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId']),
                                        confData['fieldKey'], confData['fieldKey'], fieldValue, confData['fieldKey'])
                elif confData['fieldType'] == 'CK':
                    if not bool(fieldValue):
                        checked = ""
                    else:
                        checked = "checked"
                    error = ''
                    if fieldErrors and fieldErrors.get(confData['fieldKey'], None):
                        error = 'has-error'
                    fieldHtml = """<div class="%s %s"><label><input type="checkbox" id="%s" name="%s" value="true" %s> %s</label></div>""" % (
                        fieldDivWidth, error, confData['fieldKey'], confData['fieldKey'], checked,
                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId'])
                    )
                elif confData['fieldType'] == 'IF':
                    error = ''
                    if fieldErrors and fieldErrors.get(confData['fieldKey'], None):
                        error = 'has-error'
                    if fieldValue and isinstance(fieldValue, ImageFieldFile):
                        # Show thumb image
                        imageData = base64.encodestring(fieldValue._get_file().read())
                        thumbImgHtml = """<img id="%(fieldKey)s_thumb" width="30px" height="30px" src="data:image/png;base64,%(imageData)s">
                        <button class="viewBtn btn-success btn btn-sm" field="%(fieldKey)s">
                        <i class="glyphicon glyphicon-zoom-in icon-white"></i>
                        </button>
                        <button class="deleteBtn btn-danger btn btn-sm" field="%(fieldKey)s">
                        <i class="glyphicon glyphicon-trash icon-white"></i>
                        </button>""" % {'fieldKey': confData['fieldKey'], 'imageData': imageData}
                    else:
                        thumbImgHtml = """<img id="%(fieldKey)s_thumb" width="30px" height="30px">
                        <button class="viewBtn btn-success btn btn-sm hide" field="%(fieldKey)s">
                        <i class="glyphicon glyphicon-zoom-in icon-white"></i>
                        </button>
                        <button class="deleteBtn btn-danger btn btn-sm hide" field="%(fieldKey)s">
                        <i class="glyphicon glyphicon-trash icon-white"></i>
                        </button>""" % {'fieldKey': confData['fieldKey']}
                    # Image file upload logic, upload file to UploadFilesTemp and return unique id
                    # Unique file upload id will be save in hidden field and be submitted for saving
                    fieldHtml = """
                    <script>
                    $(function(){
                        $('#%(fieldKey)s_uploadBtn').click(function (e) {
                            e.preventDefault();
                            var formData = new FormData();
                            formData.append("pageApp", "attachment");
                            formData.append("pageAction", "uploadImg");
                            formData.append("file", $("#%(fieldKey)s_file")[0].files[0]);
                            var p = $(this).parent().parent();
                            $.ajax({
                                url: "home",
                                type: "POST",
                                cache: false,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (data) {
                                    var result = jQuery.parseJSON(data);
                                    $.post("home",
                                    {
                                        pageAction: 'downloadImg',
                                        pageApp: 'attachment',
                                        pageParams: result.tempfileid
                                    }, function (data) {
                                        $("#%(fieldKey)s_thumb").attr("src", "data:image/png;base64," + data);
                                        $("#%(fieldKey)s_fileId").val(result.tempfileid)
                                        p.find(".deleteBtn").removeClass("hide");
                                        p.find(".viewBtn").removeClass("hide");
                                    });
                                },
                                error: function (data) {
                                }
                            });
                        });
                    });
                    </script>
                    """ % {'fieldKey': confData['fieldKey']}
                    fieldHtml += """<div class="%(fieldDivWidth)s %(error)s">
                    <label for="%(fieldKey)s">%(phrase1)s</label>
                    <br>
                    <div class="row">
                    <div class="col-md-4">%(thumbImgHtml)s </div>
                    <div class="col-md-6"><input id="%(fieldKey)s_file" type='file' name="file" accept=".jpg,.jpeg,.png">
                    <input id="%(fieldKey)s_fileId" type=hidden name="%(fieldKey)s">
                    </div>
                    <div class="col-md-2">
                    <button id="%(fieldKey)s_uploadBtn" class="btn btn-success btn-sm">
                    <i class="glyphicon glyphicon-upload icon-white"></i></button>
                    </div>
                    </div></div>""" % {'fieldDivWidth': fieldDivWidth, 'error': error, 'fieldKey': confData['fieldKey'],
                                       'phrase1': getPhrase(context['request'], phraseAppId, confData['labelPhraseId']),
                                       'phrase2': getPhrase(context['request'], 'g_default', 'upload'),
                                       'thumbImgHtml': thumbImgHtml}
                elif confData['fieldType'] == 'FI':
                    error = ''
                    if fieldErrors and fieldErrors.get(confData['fieldKey'], None):
                        error = 'has-error'
                    if fieldValue and isinstance(fieldValue, FieldFile):
                        # Download button
                        downloadHtml = """<button class="downloadBtn btn-success btn btn-sm" field="%(fieldKey)s">
                        <i class="glyphicon glyphicon-download icon-white"></i>
                        </button> <button class="deleteBtn btn-danger btn btn-sm" field="%(fieldKey)s">
                        <i class="glyphicon glyphicon-trash icon-white"></i>
                        </button>""" % {'fieldKey': confData['fieldKey']}
                    else:
                        downloadHtml = """<button class="downloadBtn btn-success btn btn-sm hide" field="%(fieldKey)s">
                        <i class="glyphicon glyphicon-download icon-white"></i>
                        </button> <button class="deleteBtn btn-danger btn btn-sm hide" field="%(fieldKey)s">
                        <i class="glyphicon glyphicon-trash icon-white"></i>
                        </button>""" % {'fieldKey': confData['fieldKey']}
                    # File upload logic, upload file to UploadFilesTemp and return unique id
                    # Unique file upload id will be save in hidden field and be submitted for saving
                    fieldHtml = """
                    <script>
                    $(function(){
                        $('#%(fieldKey)s_uploadBtn').click(function (e) {
                            e.preventDefault();
                            var formData = new FormData();
                            formData.append("pageApp", "attachment");
                            formData.append("pageAction", "uploadFile");
                            formData.append("file", $("#%(fieldKey)s_file")[0].files[0]);
                            var p = $(this).parent().parent();
                            $.ajax({
                                url: "home",
                                type: "POST",
                                cache: false,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (data) {
                                    var result = jQuery.parseJSON(data);
                                    $("#%(fieldKey)s_fileId").val(result.tempfileid)
                                    p.find(".deleteBtn").removeClass("hide");
                                    p.find(".downloadBtn").removeClass("hide");
                                },
                                error: function (data) {
                                }
                            });
                        });
                    });
                    </script>
                    """ % {'fieldKey': confData['fieldKey']}
                    fieldHtml += """<div class="%(fieldDivWidth)s %(error)s">
                    <label for="%(fieldKey)s">%(phrase1)s</label>
                    <br>
                    <div class="row">
                    <div class="col-md-4">
                    %(downloadHtml)s
                    </div>
                    <div class="col-md-6"><input id="%(fieldKey)s_file" type='file' name="file">
                    <input id="%(fieldKey)s_fileId" type=hidden name="%(fieldKey)s">
                    </div>
                    <div class="col-md-2">
                    <button id="%(fieldKey)s_uploadBtn" class="btn btn-success btn-sm">
                    <i class="glyphicon glyphicon-upload icon-white"></i></button>
                    </div>
                    </div></div>""" % {'fieldDivWidth': fieldDivWidth, 'error': error, 'fieldKey': confData['fieldKey'],
                                       'downloadHtml': downloadHtml,
                                       'phrase1': getPhrase(context['request'], phraseAppId, confData['labelPhraseId']),
                                       'phrase2': getPhrase(context['request'], 'g_default', 'upload')
                                       }
                elif confData['fieldType'] == 'MI':
                    addBtnHtml = ''.join(["""<a href="#" class="%s_AddBtn" """ % (confData['fieldKey'],),
                                          """><img width="20px" height="20px" src="/salesstatic/img/icon_add.png"></a><br>"""])
                    valueHtml = ''
                    # For this type, fieldValue is a list contains dict like
                    # {'id': '123', 'charValue1':'value 1', 'charValue2':'value 2'}
                    for v in fieldValue:
                        charValue1 = v['charValue1']
                        charValue2 = v['charValue2']
                        id = v['id']
                        removeBtn = """&nbsp<a href="#" class="%s_RemoveBtn" item-id="%s"><img width="20px" height="20px" src="/salesstatic/img/icon_minus.png"></a>""" % (
                            confData['fieldKey'], id
                        )
                        if charValue2:
                            valueHtml += ''.join(
                                ["""<div class="btn btn-default btn-sm">""", charValue1, "&nbsp;", charValue2, removeBtn,
                                 '</div>&nbsp'])
                        else:
                            valueHtml += ''.join(
                                ["""<div class="btn btn-default btn-sm">""", charValue1, removeBtn, '</div>&nbsp'])
                    # Change list object to json string
                    values = json.dumps(fieldValue)
                    # Then replace ' to ", since javascript recognize double quote
                    values = values.replace("'", "\"")
                    valueHtml += """<input id="%(fieldKey)s" name="%(fieldKey)s" type=hidden value='%(value)s'>""" % {
                        'fieldKey': confData['fieldKey'], 'value': values}
                    valueHtml = ''.join(
                        ["""<div id='%s_ValueDiv' class="well">""" % confData['fieldKey'], valueHtml, "</div>"])

                    subFieldHtml = ""
                    newItemJsHtml = ""
                    if confData['multipleValue1Required']:
                        subFieldHtml += """
                        <div class="col-md-6 col-xs-6">
                        <label for="%(fieldKey)s_Value1">%(phraseValue)s</label>
                        <input type="text" class="form-control" id="%(fieldKey)s_Value1" name="%(fieldKey)s_Value1"
                               placeholder="" value="">
                        </div>
                        """ % {
                            'fieldKey': confData['fieldKey'],
                            'phraseValue' : getPhrase(context['request'], phraseAppId, confData['multipleValue1PhraseId'])
                        }
                        newItemJsHtml +="""value1 = $("#%(fieldKey)s_Value1").val();""" % {
                            'fieldKey' : confData['fieldKey']
                        }
                    if confData['multipleValue2Required']:
                        subFieldHtml += """
                            <div class="col-md-6 col-xs-6">
                            <label for="%(fieldKey)s_Value2">%(phraseValue)s</label>
                            <input type="text" class="form-control" id="%(fieldKey)s_Value2" name="%(fieldKey)s_Value2"
                                   placeholder="" value="">
                            </div>
                            """ % {
                            'fieldKey': confData['fieldKey'],
                            'phraseValue': getPhrase(context['request'], phraseAppId,
                                                      confData['multipleValue2PhraseId'])
                        }
                        newItemJsHtml += """value2 = $("#%(fieldKey)s_Value2").val();""" % {
                            'fieldKey': confData['fieldKey']
                        }
                    if  confData['multipleValue1Required'] and confData['multipleValue2Required']:
                        newItemJsHtml += """
                        newItem = "<div class='btn btn-default btn-sm'>" + value1 + "&nbsp;" + value2;
                        newId = "new" + ++%(fieldKey)s_i;
                            newItem += "&nbsp;<a href='#' class='%(fieldKey)s_RemoveBtn' item-id='" + newId + "'>"
                            newItem += "<img width='20px' height='20px' src='/salesstatic/img/icon_minus.png'>"
                            newItem += "</a>"
                            newItem += "</div>&nbsp;"
                            newJsonObj = {'id': newId, 'charValue1': value1, 'charValue2': value2};
                        """ % {
                            'fieldKey': confData['fieldKey']
                        }

                    else:
                        if confData['multipleValue1Required']:
                            newItemJsHtml += """
                            newItem = "<div class='btn btn-default btn-sm'>" + value1;
                            newId = "new" + ++%(fieldKey)s_i;
                            newItem += "&nbsp;<a href='#' class='%(fieldKey)s_RemoveBtn' item-id='" + newId + "'>"
                            newItem += "<img width='20px' height='20px' src='/salesstatic/img/icon_minus.png'>"
                            newItem += "</a>"
                            newItem += "</div>&nbsp;"
                            newJsonObj = {'id': newId, 'charValue1': value1};
                            """ % {
                                'fieldKey': confData['fieldKey']
                            }

                        if confData['multipleValue2Required']:
                            newItemJsHtml += """
                            newItem = "<div class='btn btn-default btn-sm'>" + value2;
                            newId = "new" + ++%(fieldKey)s_i;
                            newItem += "&nbsp;<a href='#' class='%(fieldKey)s_RemoveBtn' item-id='" + newId + "'>"
                            newItem += "<img width='20px' height='20px' src='/salesstatic/img/icon_minus.png'>"
                            newItem += "</a>"
                            newItem += "</div>&nbsp;"
                            newJsonObj = {'id': newId, 'charValue2': value2};
                            """ % {
                                'fieldKey': confData['fieldKey']
                            }

                    scriptHtml = """
                    <div class="modal fade" id="%(fieldKey)s_Modal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel"
                         aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <button type="button" class="close" data-dismiss="modal">×</button>
                                    <h3>%(phrase)s</h3>
                                </div>
                                <div class="modal-body">
                                    <input type="hidden" id="eventId" name="eventId">
                                    <div class="row">
                                        %(subField)s
                                        <div class="clearfix" style="height:2px"></div>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <a href="#" id="%(fieldKey)s_ConfirmAddBtn" class="btn btn-primary btn-sm">%(phraseAdd)s</a>
                                    <a href="#" class="btn btn-default btn-sm"
                                       data-dismiss="modal">%(phraseClose)s</a>
                                </div>
                            </div>
                        </div>
                    </div>
                    <script>
                        $(function () {
                            $(".%(fieldKey)s_RemoveBtn").on("click", function (e) {
                            itemId = e.currentTarget.getAttribute("item-id");
                            oldValue = $("#%(fieldKey)s").val();
                            jOldValue = eval(oldValue);
                            for (var i in jOldValue) {
                                if (jOldValue[i].id == itemId) {
                                    jOldValue.splice(i, 1);
                                    $(this).parent().remove();
                                    newValue = JSON.stringify(jOldValue);
                                    $("#%(fieldKey)s").val(newValue);
                                }
                            }
                        });
                        $(".%(fieldKey)s_AddBtn").click(function (e) {
                            $('#%(fieldKey)s_Modal').modal('show');
                        });
                        $("#%(fieldKey)s_ConfirmAddBtn").click(function (e) {
                            %(newItemJs)s
                            oldValue = $("#%(fieldKey)s").val();
                            jValue = eval(oldValue);
                            jValue.push(newJsonObj);
                            newValue = JSON.stringify(jValue);
                            $("#%(fieldKey)s").val(newValue);
                            $("#%(fieldKey)s_ValueDiv").append(newItem);
                            $(".%(fieldKey)s_RemoveBtn").on("click", function (e) {
                                itemId = e.currentTarget.getAttribute("item-id");
                                oldValue = $("#%(fieldKey)s").val();
                                jOldValue = eval(oldValue);
                                for (var i in jOldValue) {
                                    if (jOldValue[i].id == itemId) {
                                        jOldValue.splice(i, 1);
                                        $(this).parent().remove();
                                        newValue = JSON.stringify(jOldValue);
                                        $("#%(fieldKey)s").val(newValue);
                                    }
                                }
                            });
                            $("#%(fieldKey)s_Value1").val('');
                            $("#%(fieldKey)s_Value2").val('');
                            $('#%(fieldKey)s_Modal').modal('hide');
                        });
                        var %(fieldKey)s_i = 0;
                        })
                    </script>
                    """ % {
                        'fieldKey': confData['fieldKey'],
                        'phrase': getPhrase(context['request'], phraseAppId, confData['labelPhraseId']),
                        # 'phraseValue1': 'value1',
                        # 'phraseValue2': 'value2',
                        'subField' : subFieldHtml,
                        'newItemJs' : newItemJsHtml,
                        'phraseAdd': getPhrase(context['request'], 'g_default', 'add'),
                        'phraseClose': getPhrase(context['request'], 'g_default', 'close')
                    }
                    fieldHtml = '<div class="%s"><label for="%s">%s</label>&nbsp;%s%s</div>%s' % (
                        fieldDivWidth, confData['fieldKey'],
                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId']),
                        addBtnHtml,
                        valueHtml,
                        scriptHtml
                    )
                else:
                    fieldHtml = ''
            else:
                # Build readonly html
                if confData['fieldType'] == 'TA':
                    fieldHtml = """<div class="%s"><label for="%s">%s</label><div class="well">%s</div></div>""" % (
                        fieldDivWidth, confData['fieldKey'],
                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId']), fieldValue)
                elif confData['fieldType'] == 'CK':
                    if not bool(fieldValue):
                        checkedHtml = """<i class="glyphicon glyphicon-remove red"></i>"""
                    else:
                        checkedHtml = """<i class="glyphicon glyphicon-ok green"></i>"""
                    fieldHtml = """<div class="%s"><label>%s %s</label></div>""" % (
                        fieldDivWidth, checkedHtml,
                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId'])
                    )
                elif confData['fieldType'] == 'IF':
                    if fieldValue and isinstance(fieldValue, ImageFieldFile):
                        imageData = base64.encodestring(fieldValue._get_file().read())
                        fieldHtml = """<div class="%(fieldDivWidth)s">
                        <label for="%(fieldKey)s">%(phrase)s</label>
                        <br>
                        <div class="">
                        <img id="%(fieldKey)s_thumb" width="30px" height="30px" src="data:image/png;base64,%(imageData)s">
                        <button class="viewBtn btn-success btn btn-sm" field="%(fieldKey)s">
                        <i class="glyphicon glyphicon-zoom-in icon-white"></i>
                        </button></div></div>""" % {'fieldDivWidth': fieldDivWidth, 'fieldKey': confData['fieldKey'],
                                                    'phrase': getPhrase(context['request'], phraseAppId,
                                                                        confData['labelPhraseId']),
                                                    'imageData': imageData}
                    else:
                        fieldHtml = """<div class="%s"><label for="%s">%s</label><div class=""><span class="label-danger label label-sm"><i
                                                    class="glyphicon glyphicon-remove icon-white"></i> %s
                                            </span></div></div>""" % (
                            fieldDivWidth, confData['fieldKey'],
                            getPhrase(context['request'], phraseAppId, confData['labelPhraseId']),
                            getPhrase(context['request'], 'g_default', 'noImage')
                        )
                elif confData['fieldType'] == 'FI':
                    if fieldValue and isinstance(fieldValue, FieldFile):
                        filename = fieldValue._get_path().split('/')[-1]
                        filepath = fieldValue._get_path()
                        context['request'].session['%s_file' % confData['fieldKey']] = {'filename': filename,
                                                                                        'filepath': filepath}
                        fieldHtml = """<div class="%(fieldDivWidth)s">
                        <label for="%(fieldKey)s">%(phrase)s</label>
                        <br>
                        <div class="">
                        <button class="downloadBtn btn-success btn btn-sm" field="%(fieldKey)s">
                        <i class="glyphicon glyphicon-download icon-white"></i>
                        </button> %(filename)s</div></div>""" % {'fieldDivWidth': fieldDivWidth,
                                                                 'fieldKey': confData['fieldKey'],
                                                                 'phrase': getPhrase(context['request'], phraseAppId,
                                                                                     confData['labelPhraseId']),
                                                                 'filename': filename
                                                                 }
                    else:
                        fieldHtml = """<div class="%s"><label for="%s">%s</label><div class=""><span class="label-danger label label-sm"><i
                                                    class="glyphicon glyphicon-remove icon-white"></i> %s
                                            </span></div></div>""" % (
                            fieldDivWidth, confData['fieldKey'],
                            getPhrase(context['request'], phraseAppId, confData['labelPhraseId']),
                            getPhrase(context['request'], 'g_default', 'noFile')
                        )
                elif confData['fieldType'] == 'LK':
                    fieldHtml = """<div class="%(fieldDivWidth)s"><label for="%(fieldKey)s">%(phrase)s</label>
                    <div class="form-control-blank">%(link)s</div>
                    </div>""" % {
                        'fieldDivWidth': fieldDivWidth,
                        'fieldKey': confData['fieldKey'],
                        'phrase': getPhrase(context['request'], phraseAppId, confData['labelPhraseId']),
                        'link': confData.get('fieldTypeLKHtml', 'No link')
                    }
                elif confData['fieldType'] == 'MI':
                    valueHtml = ''
                    # # For this type, fieldValue is a list contains dict like
                    # # {'charValue1':'value 1', 'charValue2':'value 2'}
                    for v in fieldValue:
                        charValue1 = v['charValue1']
                        charValue2 = v['charValue2']
                        if charValue2:
                            valueHtml += ''.join(
                                ["""<div class="btn btn-default btn-sm">""", charValue1, "&nbsp;", charValue2,
                                 '</div>&nbsp'])
                        else:
                            valueHtml += ''.join(
                                ["""<div class="btn btn-default btn-sm">""", charValue1, '</div>&nbsp'])
                    values = json.dumps(fieldValue)
                    valueHtml = ''.join(["""<div class="well">""", valueHtml, "</div>"])
                    fieldHtml = '<div class="%s"><label for="%s">%s</label><br>%s</div>' % (
                        fieldDivWidth, confData['fieldKey'],
                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId']),
                        valueHtml
                    )
                else:
                    fieldHtml = """<div class="%s"><label for="%s">%s</label><input type="text" class="form-control" name="%s" placeholder="" value="%s" readonly></div>""" % (
                        fieldDivWidth, confData['fieldKey'],
                        getPhrase(context['request'], phraseAppId, confData['labelPhraseId']), confData['fieldKey'],
                        displayValue)
            html = ''.join([html, fieldHtml])
        html = ''.join([html, "</div>"])
        imageViewHtml = """
        <div class="modal" id="imageViewModal" tabindex="-1" role="dialog" aria-labelledby="imgModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-body">
                        <div class="row" id="bigImg">
                            <div class="col-md-12 col-xs-12">
                                <img id="bigImage" width="100%%" height="100%%">
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-default btn-sm"
                                data-dismiss="modal">%(close)s</button>
                    </div>
                </div>
            </div>
        </div>
        <script>
        $(function(){
            $('.viewBtn').click(function(e){
                e.preventDefault();
                var f = e.currentTarget.getAttribute('field');
                var s = $('#'+f+'_thumb').attr("src");
                $("#bigImage").attr("src",s);
                $("#imageViewModal").modal("show");
            });
            $('.downloadBtn').click(function(e){
                e.preventDefault();
                var f = e.currentTarget.getAttribute('field');
                toNav("attachment","downloadFile",f,"","N");
            });
            $('.deleteBtn').click(function(e){
                e.preventDefault();
                var f = e.currentTarget.getAttribute('field');
                $('#'+f+'_fileId').val(0);
                $('#'+f+'_thumb').attr("src","");
                var p = $(this).parent().parent();
                p.find('.downloadBtn').addClass("hide");
                p.find('.viewBtn').addClass("hide");
                $(this).addClass("hide");
            })
        })
        </script>
        """ % {'close': getPhrase(context['request'], 'g_default', 'close')}
        html = ''.join([imageViewHtml, html])
        t = Template(html)
        html = t.render(context)
        return html

    def buildSearchFields(self, context, entityType):
        if entityType == 'Order':
            vContext = getContext(context['request'], coCtxName)
            appName = 'commonOrder'
            vEntityType = vContext.orderType
            phraseAppId = 'order'
        elif entityType == 'BP':
            vContext = getContext(context['request'], cbCtxName)
            appName = 'commonBp'
            vEntityType = vContext.bpType
            phraseAppId = 'bp'
        if vContext is None:
            return ''
        finalHtml = ''
        if not vEntityType:
            types = vContext.searchBean.getSelectOption('type')
            if len(types) == 1:
                vEntityType = types[0].low
        custSrchFields = False
        if vEntityType:
            if entityType == 'Order':
                # Check whether search fields is configured
                fieldsOfOrder = OrderFieldDef.objects.filter(Q(orderType=vEntityType))
                configuredFields = StdViewLayoutConf.objects.filter(field__in=fieldsOfOrder, visibility=True,
                                                                    viewType__key='Search', valid=True).order_by(
                    'locRow', 'locCol')
            elif entityType == 'BP':
                fieldsOfBP = BPFieldDef.objects.filter(Q(bpType=vEntityType))
                configuredFields = BPStdViewLayoutConf.objects.filter(field__in=fieldsOfBP, visibility=True,
                                                                      viewType__key='Search', valid=True).order_by(
                    'locRow',
                    'locCol')
            if configuredFields.count() > 0:
                custSrchFields = True
        searchFieldOptions = {}
        if entityType == 'Order':
            searchFieldOptions['id'] = {'k': 'id', 'v': getPhrase(context['request'], phraseAppId, 'id')}
            searchFieldOptions['type'] = {'k': 'type', 'v': getPhrase(context['request'], phraseAppId, 'type'),
                                          'ft': 'SE'}
            searchFieldOptions['description'] = {'k': 'description',
                                                 'v': getPhrase(context['request'], phraseAppId, 'shortName'),
                                                 'ft': 'IN'}
            searchFieldOptions['createdAt'] = {'k': 'createdAt',
                                               'v': getPhrase(context['request'], phraseAppId, 'createdAt')}
            searchFieldOptions['createdBy'] = {'k': 'createdBy',
                                               'v': getPhrase(context['request'], phraseAppId, 'createdBy')}
            searchFieldOptions['updatedAt'] = {'k': 'updatedAt',
                                               'v': getPhrase(context['request'], phraseAppId, 'updatedAt')}
            searchFieldOptions['updatedBy'] = {'k': 'updatedBy',
                                               'v': getPhrase(context['request'], phraseAppId, 'updatedBy')}
            searchFieldOptions['status'] = {'k': 'status', 'v': getPhrase(context['request'], phraseAppId, 'status'),
                                            'ft': 'SE'}
            searchFieldOptions['priority'] = {'k': 'priority',
                                              'v': getPhrase(context['request'], phraseAppId, 'priority'),
                                              'ft': 'SE'}
        elif entityType == 'BP':
            searchFieldOptions['id'] = {'k': 'id', 'v': getPhrase(context['request'], phraseAppId, 'id')}
            searchFieldOptions['type'] = {'k': 'type', 'v': getPhrase(context['request'], phraseAppId, 'type'),
                                          'ft': 'SE'}
            searchFieldOptions['firstName'] = {'k': 'firstName',
                                               'v': getPhrase(context['request'], phraseAppId, 'firstName'),
                                               'ft': 'IN'}
            searchFieldOptions['middleName'] = {'k': 'middleName',
                                                'v': getPhrase(context['request'], phraseAppId, 'middleName'),
                                                'ft': 'IN'}
            searchFieldOptions['lastName'] = {'k': 'lastName',
                                              'v': getPhrase(context['request'], phraseAppId, 'lastName'),
                                              'ft': 'IN'}
            searchFieldOptions['name1'] = {'k': 'name1',
                                           'v': getPhrase(context['request'], phraseAppId, 'name1'),
                                           'ft': 'IN'}
            searchFieldOptions['name2'] = {'k': 'name1',
                                           'v': getPhrase(context['request'], phraseAppId, 'name2'),
                                           'ft': 'IN'}
        if custSrchFields:
            # Build search fields option based on order type
            for cf in configuredFields:
                phraseId = cf.labelPhraseId
                if not phraseId:
                    phraseId = cf.field.fieldKey
                phrase = getPhrase(context['request'], phraseAppId, phraseId)
                searchFieldOption = {}
                # Field key
                searchFieldOption['k'] = cf.field.fieldKey
                # Field value / Description / Name
                searchFieldOption['v'] = phrase
                # Field value type: String, Boolean etc
                searchFieldOption['ft'] = cf.field.fieldType.key
                searchFieldOption['vt'] = cf.field.valueType
                searchFieldOption['sk'] = cf.field.storeKey
                searchFieldOption['st'] = cf.field.storeType
                # Append order specified field to list
                searchFieldOptions[cf.field.fieldKey] = searchFieldOption
        criteriaList = vContext.searchBean.getList()
        for i in range(0, len(criteriaList)):
            criteria = criteriaList[i]
            # Continue to next if field not in search list
            # This could be caused by changing order type, the previous field is no longer valid
            if searchFieldOptions.get(criteria.field, None) is None:
                continue
            # Build fields dropdown selection
            fn = 'fn%d' % i
            html = buildSelectionOption2(fn, searchFieldOptions, criteria.field,
                                         "javascript:toNavWith('f','%s','search','crchg')" % (appName,))
            html = ''.join(['<div class="col-md-2">', html, '</div>'])
            # Build options based on field value type
            fieldType = searchFieldOptions[criteria.field].get('ft', None)
            valueType = searchFieldOptions[criteria.field].get('vt', None)
            storeKey = searchFieldOptions[criteria.field].get('sk', None)
            storeType = searchFieldOptions[criteria.field].get('st', None)
            fo = 'fo%d' % i
            if criteria.field == 'type':
                entityOptOptions = {}
                o = 'eq'
                entityOptOptions[o] = {'k': o, 'v': getPhrase(context['request'], 'g_default', o)}
            else:
                entityOptOptions = GetFieldOptByType(fieldType, valueType, context)
            html2 = buildSelectionOption2(fo, entityOptOptions, criteria.opt,
                                          "javascript:toNavWith('f','%s','search','crchg')" % (appName,))
            lan = context['request'].session.get('lan', 'cn')
            if lan == 'cn':
                w = 1
            else:
                w = 2
            html2 = ''.join(['<div class="col-md-', str(w), '">', html2, '</div>'])
            fl = 'fl%d' % i
            if criteria.field == 'type':
                # Selection for types
                if entityType == 'Order':
                    typeList = []
                    for ot in OrderType.objects.all():
                        typeItem = {}
                        authName = 'Order_%s_Access' % ot.key
                        (_, canView, _, _) = getUserAuthorization(context, authName)
                        if canView:
                            typeItem['key'] = ot.key
                            typeItem['description'] = ot.description
                            typeList.append(typeItem)
                    opts = [{'k': t['key'], 'v': t['description']} for t in typeList]
                    # if len(typeList) > 0:
                    #     opts.insert(0, {'k': '', 'v': ''})
                elif entityType == 'BP':
                    typeList = []
                    for bt in BPType.objects.filter(~Q(key='ZZ')):
                        typeItem = {}
                        authName = 'BP_%s_Access' % bt.key
                        (_, canView, _, _) = getUserAuthorization(context, authName)
                        if canView:
                            typeItem['key'] = bt.key
                            typeItem['description'] = bt.description
                            typeList.append(typeItem)
                    opts = [{'k': t['key'], 'v': t['description']} for t in typeList]
                    # if len(typeList) > 0:
                    #     opts.insert(0, {'k': '', 'v': ''})
                html3 = buildSelectionOption(fl, opts, criteria.low,
                                             "javascript:toNavWith('f','%s','search','crchg')" % (appName,))
            elif criteria.field == 'status':
                if entityType == 'Order':
                    opts = [{'k': t.key, 'v': t.description} for t in
                            StatusType.objects.filter(orderType__key=vEntityType)]
                    opts.insert(0, {'k': '', 'v': ''})
                    html3 = buildSelectionOption(fl, opts, criteria.low, None)
            elif criteria.field == 'priority':
                if entityType == 'Order':
                    opts = [{'k': t.key, 'v': t.description} for t in
                            PriorityType.objects.filter(orderType__key=vEntityType)]
                    opts.insert(0, {'k': '', 'v': ''})
                    html3 = buildSelectionOption(fl, opts, criteria.low, None)
            elif criteria.field == 'createdBy' or criteria.field == 'updatedBy':
                if entityType == 'Order':
                    opts = [{'k': t.id, 'v': t.displayName()} for t in BP.objects.filter(type='IN')]
                    opts.insert(0, {'k': '', 'v': ''})
                    html3 = buildSelectionOption(fl, opts, criteria.low, None)
            else:
                if fieldType == 'SE':
                    # Selection type
                    if entityType == 'Order':
                        beName = 'OrderBE'
                        # Get options from BusinessEntity
                        if vEntityType:
                            beObj = OrderBEDef.objects.filter(orderType__key=vEntityType)
                            if beObj:
                                beName = beObj[0].businessEntity
                        order = Order()
                        order.type = OrderType.objects.get(pk=vEntityType)
                        be = eval("%s(order)" % beName)
                    elif entityType == 'BP':
                        beName = 'BPBE'
                        # Get options from BusinessEntity
                        if vEntityType:
                            beObj = BPBEDef.objects.filter(bpType__key=vEntityType)
                            if beObj:
                                beName = beObj[0].businessEntity
                        bp = BP()
                        bp.type = BPType.objects.get(pk=vEntityType)
                        be = eval("%s(bp)" % beName)
                    if hasattr(be, 'get_%s_options' % criteria.field):
                        fieldOptions = eval("be.get_%s_options()" % criteria.field)
                        fopts = [{'k': k, 'v': v} for k, v in fieldOptions.items()]
                        fopts.insert(0, {'k': '', 'v': ''})
                        html3 = buildSelectionOption(fl, fopts, criteria.low, None)
                    elif storeKey and storeType == 'Customized':
                        if entityType == 'Order':
                            # Get options from OrderExtSelectionFieldType by storeKey
                            fopts = [{'k': option.key, 'v': option.description} for option in
                                     OrderExtSelectionFieldType.objects.filter(orderType=vEntityType,
                                                                               fieldKey=storeKey)]
                            fopts.insert(0, {'k': '', 'v': ''})
                            html3 = buildSelectionOption(fl, fopts, criteria.low, None)
                    else:
                        html3 = buildInputBox(fl, '', criteria.low)
                elif fieldType == 'DA':
                    # Date type
                    html3 = buildDateInputBox(fl, '', criteria.low)
                    if criteria.opt == 'bt':
                        fh = 'fh%d' % i
                        html4 = buildDateInputBox(fh, '', criteria.high)
                        html3 = ''.join([html3, html4])
                elif fieldType == 'DT':
                    # Date type
                    html3 = buildDateTimeInputBox(fl, '', criteria.low)
                    if criteria.opt == 'bt':
                        fh = 'fh%d' % i
                        html4 = buildDateTimeInputBox(fh, '', criteria.high)
                        html3 = ''.join([html3, html4])
                else:
                    html3 = buildInputBox(fl, '', criteria.low)
                    if criteria.opt == 'bt':
                        fh = 'fh%d' % i
                        html4 = buildInputBox(fh, '', criteria.high)
                        html3 = ''.join([html3, html4])
            html3 = ''.join(['<div class="col-md-4">', html3, '</div>'])

            html = ''.join([html, html2, html3])
            html = ''.join(["<div class='row'>", html, '</div>'])
            finalHtml = ''.join([finalHtml, html, html_separator])
        return finalHtml

    def buildSearchResult(self, context, entityType):
        if entityType == 'Order':
            ctxName = coCtxName
            appName = 'commonOrder'
            phraseAppId = 'order'
        elif entityType == 'BP':
            ctxName = cbCtxName
            appName = 'commonBp'
            phraseAppId = 'bp'
        vContext = getContext(context['request'], ctxName)
        reids = vContext.reids
        if not reids or len(reids) == 0:
            return ''
        if entityType == 'Order':
            entities = Order.objects.filter(deleteFlag=False, id__in=reids)
        elif entityType == 'BP':
            entities = BP.objects.filter(deleteFlag=False, id__in=reids)
        vEntityType = None
        entityFormat = False
        # Check result order type
        # If only one type in result, render result by configuration
        v = entities.values('type').distinct()
        if len(v) == 1:
            vEntityType = v[0]['type']
        if vEntityType:
            if entityType == 'Order':
                fieldsOfOrder = OrderFieldDef.objects.filter(orderType=vEntityType)
                configuredFields = StdViewLayoutConf.objects.filter(field__in=fieldsOfOrder, visibility=True,
                                                                    viewType__key='Result', valid=True).order_by(
                    'locRow', 'locCol')
            elif entityType == 'BP':
                fieldsOfBP = BPFieldDef.objects.filter(bpType=vEntityType)
                configuredFields = BPStdViewLayoutConf.objects.filter(field__in=fieldsOfBP, visibility=True,
                                                                      viewType__key='Result', valid=True).order_by(
                    'locRow',
                    'locCol')
            if configuredFields.count() > 0:
                entityFormat = True
        if entityType == 'Order':
            beName = 'OrderBE'
            headerColumn = ['id', 'type', 'description', 'status', 'priority', 'createdAt', 'createdBy', 'updatedAt',
                            'updatedBy']
        elif entityType == 'BP':
            beName = 'BPBE'
            headerColumn = ['id', 'type', 'firstName', 'middleName', 'lastName', 'name1', 'name2']
        headerColumnPhrase = []
        records = []
        # Build html and store data in session
        headerWidthDic = {}
        headHtml = ''
        bodyHtml = ''
        if entityFormat:
            if entityType == 'Order':
                beObj = OrderBEDef.objects.filter(orderType__key=vEntityType)
            elif entityType == 'BP':
                beObj = BPBEDef.objects.filter(bpType__key=vEntityType)
            if beObj:
                beName = beObj[0].businessEntity
            headerColumn = []
            for cf in configuredFields:
                headerColumn.append(cf.field.fieldKey)
                # Set width in dict if available
                if cf.locWidth is not None:
                    headerWidthDic[cf.field.fieldKey] = cf.locWidth
                hp = cf.labelPhraseId
                if not hp:
                    hp = cf.field.fieldKey
                columnName = getPhrase(context['request'], phraseAppId, hp)
                # Store in session 'rh'
                headerColumnPhrase.append(columnName)
                # Build header html
                columnHtml = ''.join(['<th>', columnName, '</th>'])
                headHtml = ''.join([headHtml, columnHtml])
        else:
            for h in headerColumn:
                columnName = getPhrase(context['request'], phraseAppId, h)
                headerColumnPhrase.append(columnName)
                columnHtml = ''.join(['<th>', columnName, '</th>'])
                headHtml = ''.join([headHtml, columnHtml])

        # Got customized page length by configuration key searchResultTable_pageLength
        # Default is 50
        uid = context['request'].session['up']['userloginid']
        if entityType == 'Order':
            parameterName = 'searchResultTable_pageLength'
        elif entityType == 'BP':
            parameterName = 'searchBPResultTable_pageLength'
        up = UserParameter.objects.filter(userlogin_id=uid, name=parameterName)
        if up:
            up = up[0]
            pageLength = int(up.value)
        else:
            pageLength = 50
        # JQuery
        dataTableHtml = """
        <script>
         $(document).ready(function () {
           $('#searchResultTable').dataTable({
             %s
             "aaSorting":[],
             "pageLength": %d
           });
           $('#searchResultTable').on( 'length.dt', function ( e, settings, len ) {
             $.post("ajax", {
               t:'up',
               n:'%s',
               v:len
             }, function (data,result) {
               var jsonData = jQuery.parseJSON(data);
               if (result != 'success' || jsonData.code != 0){
                 alert('save error')
               }
             });
           });
         });
         </script>
                   """ % (getPhrase(context['request'], 'g_default', 'dataTableComm'), pageLength, parameterName)

        # Complete header html
        headHtml = ''.join([dataTableHtml,
                            """<table id="searchResultTable" class="table table-striped table-condensed table-bordered bootstrap-datatable responsive"><thead><tr>""",
                            headHtml, """</thead><tbody>"""])

        if entityFormat:
            for entity in entities:
                be = eval("%s(%s)" % (beName, 'entity'))
                record = [''] * len(headerColumn)
                recordHtml = ''
                for cf in configuredFields:
                    confData = GetFieldConfigData(be, cf)
                    fieldValue, displayValue = GetFieldValue(be, **confData)
                    # Store in session
                    record[headerColumn.index(cf.field.fieldKey)] = displayValue
                    # Build html
                    tdwidth = headerWidthDic.get(cf.field.fieldKey, None)
                    if tdwidth:
                        tdwidth = ''.join(["""<td width='""", tdwidth, """'>"""])
                    else:
                        tdwidth = '<td>'
                    if cf.field.fieldKey == 'id':
                        columnHtml = ''.join(
                            [tdwidth, """<a href="#" onclick="toNavWith('f','%s','view','""" % (appName,),
                             str(displayValue),
                             """')">""", str(displayValue), '</td>'])
                    else:
                        columnHtml = ''.join([tdwidth, str(displayValue), '</td>'])
                    recordHtml = ''.join([recordHtml, columnHtml])
                records.append(record)
                bodyHtml = ''.join([bodyHtml, '<tr>', recordHtml, '</tr>'])
        else:
            for entity in entities:
                be = eval("%s(%s)" % (beName, 'entity'))
                record = [''] * len(headerColumn)
                recordHtml = ''
                for fieldKey in headerColumn:
                    fieldValue, displayValue = GetFieldValue(be, **{'fieldKey': fieldKey})
                    # Store in session
                    record[headerColumn.index(fieldKey)] = displayValue

                    # Build html
                    tdwidth = headerWidthDic.get(fieldKey, None)
                    if tdwidth:
                        tdwidth = ''.join(["""<td width='""", tdwidth, """'>"""])
                    else:
                        tdwidth = '<td>'
                    if fieldKey == 'id':
                        columnHtml = ''.join(
                            [tdwidth, """<a href="#" onclick="toNavWith('f','%s','view','""" % (appName,),
                             str(displayValue),
                             """')">""", str(displayValue), '</td>'])
                    else:
                        columnHtml = ''.join([tdwidth, str(displayValue), '</td>'])
                    recordHtml = ''.join([recordHtml, columnHtml])
                records.append(record)
                bodyHtml = ''.join([bodyHtml, '<tr>', recordHtml, '</tr>'])
        bodyHtml = ''.join([headHtml, bodyHtml, '</tbody></table>'])
        vContext.resultHeaders = headerColumnPhrase
        vContext.resultItems = records
        setContext(context['request'], ctxName, vContext)
        return bodyHtml

    def buildSavedSearchFields(self, context, entityType):
        if entityType == 'Order':
            appName = 'commonOrder'
            vContext = getContext(context['request'], coCtxName)
        elif entityType == 'BP':
            appName = 'commonBp'
            vContext = getContext(context['request'], cbCtxName)
        else:
            appName = ''
        uid = context['request'].session['up']['userloginid']
        userLogin = UserLogin.objects.get(id=uid)
        opts = [{'k': t['name'], 'v': t['name']} for t in
                UserSavedSearchFavorite.objects.filter(userlogin=userLogin, type=appName).values(
                    "name").distinct()
                ]
        opts.insert(0, {'k': '', 'v': ''})
        html = buildSelectionOption('savedName', opts, vContext.savedName,
                                    "javascript:toNavWith('f','%s','search','savsf')" % (appName,))
        delSavedSrhBtnHtml = """
            <button class="btn btn-danger btn-sm glyphicon glyphicon-trash" onclick="javascript:toNavWith('f','%s','search','csrmv')"></button>""" % (
            appName,)
        html = ''.join(
            [getPhrase(context['request'], 'g_default', 'savedSearch'), '&nbsp;', html, delSavedSrhBtnHtml])
        html = ''.join(['<div class="col-md-5">', html, '</div>'])
        html = ''.join(["<div class='row'>", html, '</div>'])
        html = ''.join([html, html_separator])
        return html

    def buildAttachment(self, context, entityType):
        canEdit = False
        if entityType == 'Order':
            vContext = getContext(context['request'], coCtxName)
            appName = 'commonOrder'
            phraseAppId = 'order'
            attachments = OrderFileAttachment.objects.filter(order__id=vContext.orderId, deleteFlag=False).order_by(
                '-createdAt')
            vContext = getContext(context['request'], coCtxName)
            if vContext.orderType:
                # Check whether user has access to edit this kind of order
                authName = 'Order_%s_Access' % vContext.orderType
                (_, _, canEdit, _) = getUserAuthorization(context, authName)
        elif entityType == 'BP':
            vContext = getContext(context['request'], cbCtxName)
            appName = 'commonBp'
            phraseAppId = 'bp'
            attachments = BPFileAttachment.objects.filter(bp__id=vContext.bpId, deleteFlag=False).order_by(
                '-createdAt')
            vContext = getContext(context['request'], cbCtxName)
            if vContext.bpType:
                # Check whether user has access to edit this kind of order
                authName = 'BP_%s_Access' % vContext.bpType
                (_, _, canEdit, _) = getUserAuthorization(context, authName)
        else:
            attachments = None
        if attachments:
            # Build attachment info
            pageStatus = context['nav']['pageStatus']
            if pageStatus == 'edit':
                showDelete = True
            else:
                showDelete = False
            myBP = getCurrentUserBp(context['request'])
            headers = [
                getPhrase(context['request'], 'g_default', 'filename', u'文件'),
                getPhrase(context['request'], 'g_default', 'createdBy', u'创建者'),
                getPhrase(context['request'], 'g_default', 'createdAt', u'创建时间'),
                getPhrase(context['request'], 'g_default', 'operation', u'操作')
            ]
            if canEdit:
                headHtml = """<button class="btn btn-primary btn-sm"
            onclick="javascript:toNavWith('f','commonOrder','edit','1')">%s</button>
    <div class="clearfix"><br></div>""" % getPhrase(context['request'], 'g_default', 'edit')
            else:
                headHtml = ''
            for h in headers:
                headHtml = ''.join([headHtml, "<td>", h, "</td>"])
            headHtml = ''.join([
                """<table class="table table-striped table-condensed table-bordered bootstrap-datatable datatable responsive"><thead><tr>""",
                headHtml, """</tr></thead><tbody>"""])
            bodyHtml = ''
            for attachment in attachments:
                filename = attachment.name
                createdBy = attachment.createdBy.displayName()
                createdAt = timezone.localtime(attachment.createdAt)
                createdAt = str(createdAt.strftime("%Y-%m-%d %H:%M:%S"))
                downloadOpt = """<a class="btn btn-success btn-sm" href="javascript:toNav('%s','download','%s','','N')"><i class="glyphicon glyphicon-download icon-white"></i>  %s</a>""" % (
                    appName, attachment.id, getPhrase(context['request'], 'g_default', 'download'))
                deleteOpt = """<button type="button" class="btn btn-danger btn-sm" data-toggle="modal" data-target="#fileDelModal" data-whatever="%s"><i class="glyphicon glyphicon-trash icon-white"></i> %s </button>""" % (
                    attachment.id, getPhrase(context['request'], 'g_default', 'delete'))
                if showDelete and attachment.createdBy == myBP:
                    operation = ''.join([downloadOpt, '&nbsp;', deleteOpt])
                else:
                    operation = ''.join([downloadOpt])

                bodyHtml = ''.join([bodyHtml,
                                    "<tr><td>", filename, "</td>",
                                    "<td>", createdBy, "</td>",
                                    "<td>", createdAt, "</td>",
                                    "<td>", operation, "</td></tr>"])
            html = ''.join([headHtml, bodyHtml, "</tbody></table>"])
        else:
            html = '未上传任何文件'
        return html

    def buildChangeLog(self, context, entityType):
        html = ''
        if entityType == 'Order':
            vContext = getContext(context['request'], coCtxName)
            phraseAppId = 'order'
        elif entityType == 'BP':
            vContext = getContext(context['request'], cbCtxName)
            phraseAppId = 'bp'
        if vContext.changeLog:
            headers = [
                getPhrase(context['request'], 'g_default', 'field', u'字段'),
                getPhrase(context['request'], 'g_default', 'oldValue', u'旧值'),
                getPhrase(context['request'], 'g_default', 'newValue', u'新值'),
                getPhrase(context['request'], 'g_default', 'updatedBy', u'更新者'),
                getPhrase(context['request'], 'g_default', 'updatedAt', u'更新时间')
            ]
            headHtml = ''
            for h in headers:
                headHtml = ''.join([headHtml, "<td>", h, "</td>"])
            headHtml = ''.join([
                """<table class="table table-striped table-condensed table-bordered bootstrap-datatable datatable responsive"><thead><tr>""",
                headHtml, """</tr></thead><tbody>"""])
            bodyHtml = ''
            for log in vContext.changeLog:
                fieldname = getPhrase(context['request'], phraseAppId, log.objectField)
                updatedBy = BP.objects.get(id=log.updatedBy).displayName()
                updatedAt = timezone.localtime(log.updatedAt)
                updatedAt = str(updatedAt.strftime("%Y-%m-%d %H:%M:%S"))
                bodyHtml = ''.join([bodyHtml,
                                    "<tr><td>", fieldname, "</td>",
                                    "<td>", str(log.oldValue), "</td>",
                                    "<td>", str(log.newValue), "</td>",
                                    "<td>", updatedBy, "</td>",
                                    "<td>", updatedAt, "</td></tr>"])
            html = ''.join([headHtml, bodyHtml, "</tbody></table>"])
        return html

    def buildOrderRelation(self, context):
        vContext = getContext(context['request'], coCtxName)
        if vContext.orderId:
            orderRel = OrderRelation.objects.filter(orderA=Order.objects.get(id=vContext.orderId), relation='FL',
                                                    valid=True)
        followUps = [o.orderB for o in orderRel]
        if followUps:
            headers = [
                getPhrase(context['request'], 'g_default', 'id', u'ID'),
                getPhrase(context['request'], 'g_default', 'type', u'类型'),
                getPhrase(context['request'], 'g_default', 'description', u'描述'),
                getPhrase(context['request'], 'g_default', 'checkResult', u'结果'),
                getPhrase(context['request'], 'g_default', 'createdAt', u'创建时间')
            ]
            headHtml = ''
            for h in headers:
                headHtml = ''.join([headHtml, "<td>", h, "</td>"])
            headHtml = ''.join([
                """<table class="table table-striped table-condensed table-bordered bootstrap-datatable datatable responsive"><thead><tr>""",
                headHtml, """</tr></thead><tbody>"""])
            bodyHtml = ''
            for followUp in followUps:
                orderId = followUp.id
                link = """<a href="javascript:toNav('commonOrder','view','%(orderId)s','')">%(orderId)s</a>""" % {
                    'orderId': orderId}
                orderType = followUp.type.description
                createdAt = timezone.localtime(followUp.createdAt)
                createdAt = str(createdAt.strftime("%Y-%m-%d %H:%M:%S"))
                if followUp.ordercustomized.checkResult:
                    checkResultDesc = OrderExtSelectionFieldType.objects.filter(orderType=followUp.type,
                                                                                key=followUp.ordercustomized.checkResult)[
                        0].description
                else:
                    checkResultDesc = ''
                bodyHtml = ''.join([bodyHtml,
                                    "<tr><td>", link, "</td>",
                                    "<td>", orderType, "</td>",
                                    "<td>", followUp.description, "</td>",
                                    "<td>", checkResultDesc, "</td>",
                                    "<td>", createdAt, "</td></tr>"])
            html = ''.join([headHtml, bodyHtml, "</tbody></table>"])
        else:
            html = '无'
        return html

    def render(self, context):
        if self.name == 'buildViewHistory':
            return self.buildViewHistory(context)
        elif self.name == 'buildToolbar':
            return self.buildToolbar(context, 'Order')
        elif self.name == 'buildBPToolbar':
            return self.buildToolbar(context, 'BP')
        elif self.name == 'buildResultToolbar':
            return self.buildResultToolbar(context, 'Order')
        elif self.name == 'buildBPResultToolbar':
            return self.buildResultToolbar(context, 'BP')
        elif self.name == 'buildFields':
            return self.buildFields(context, 'Order')
        elif self.name == 'buildBPFields':
            return self.buildFields(context, 'BP')
        elif self.name == 'buildSearchFields':
            return self.buildSearchFields(context, 'Order')
        elif self.name == 'buildBPSearchFields':
            return self.buildSearchFields(context, 'BP')
        elif self.name == 'buildSearchResult':
            return self.buildSearchResult(context, 'Order')
        elif self.name == 'buildBPSearchResult':
            return self.buildSearchResult(context, 'BP')
        elif self.name == 'buildSavedSearchField':
            return self.buildSavedSearchFields(context, 'Order')
        elif self.name == 'buildBPSavedSearchField':
            return self.buildSavedSearchFields(context, 'BP')
        elif self.name == 'buildOrderAttachment':
            return self.buildAttachment(context, 'Order')
        elif self.name == 'buildBPAttachment':
            return self.buildAttachment(context, 'BP')
        elif self.name == 'buildOrderChangeLog':
            return self.buildChangeLog(context, 'Order')
        elif self.name == 'buildBPChangeLog':
            return self.buildChangeLog(context, 'BP')
        elif self.name == 'buildOrderRelation':
            return self.buildOrderRelation(context)
        elif self.name == 'buildOAInfo':
            html = ''
            coContext = getContext(context['request'], coCtxName)
            (stageKey, _) = coContext.currentOrder.get_stage()
            if stageKey != '00004':
                html = '仅在山航签约下有OA信息'
                return html
            # Stage is 00004
            html = """

            <a href="#" onclick="toNavWith('f','commonOrder','view','303')">test</a>
            """

            return html


@register.tag(name='UtilTag')
def utilTag(parse, token):
    # log.info('phrase tag initialized')
    try:
        tag_name, name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly 2 arguments: appId and phraseId" % \
            token.split_contents[0]
    return UtilTag(name)
