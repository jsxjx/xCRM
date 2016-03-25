from django import template
from crm.models import OrderType, StatusType, PriorityType, OrderExtSelectionFieldType, DistrictType, BPRelation, \
    BPRelType
from crm.common import *

register = template.Library()


class FieldSelectTag(template.Node):
    def render(self, context):
        options = ""
        self.value = self.value.resolve(context)
        # return self.value
        ot = OrderType.objects.filter(key__exact=self.orderType)
        if ot:
            ot = ot[0]
        if self.fieldType == 'status':
            options = ''.join([('<option value="%s" %s>%s</option>' % (
                s.key, bool(s.key == self.value) and """ selected ="selected" """ or "", s.description)) for s in
                               StatusType.objects.filter(orderType__exact=ot)])
        if self.fieldType == 'priority':
            options = ''.join([('<option value="%s" %s>%s</option>' % (
                s.key, bool(s.key == self.value) and """ selected = "selected" """ or "", s.description)) for s in
                               PriorityType.objects.filter(orderType__exact=ot)])
        if self.fieldType == 'ext':
            options = ''.join([('<option value="%s" %s>%s</option>' % (
                s.key, bool(s.key == self.value) and """ selected = "selected" """ or "", s.description)) for s in
                               OrderExtSelectionFieldType.objects.filter(orderType=ot, fieldKey=self.extKey)])
        if self.fieldType == 'district':
            options = ''.join([('<option value="%s" %s>%s</option>' % (
                s.key, bool(s.key == self.value) and """ selected = "selected" """ or "", s.description)) for s in
                               DistrictType.objects.all()])
        if self.fieldType == 'customer':
            options = ''.join([('<option value="%s" %s>%s</option>' % (
                bpr.bpB.id, bool(str(bpr.bpB.id) == str(self.value)) and """ selected = "selected" """ or "",
                bpr.bpB.name1)) for bpr in BPRelation.objects.filter(relation__exact='C1')])
        if self.fieldType == 'channel':
            options = ''.join([('<option value="%s" %s>%s</option>' % (
                bpr.bpB.id, bool(str(bpr.bpB.id) == str(self.value)) and """ selected = "selected" """ or "",
                bpr.bpB.name1)) for bpr in BPRelation.objects.filter(relation__exact='TM')])
        if self.fieldType == 'empResp':
            # options = ''.join([('<option value="%s" %s>%s</option>' % (
            # bpr.bpB.id, bool(str(bpr.bpB.id) == str(self.value)) and """ selected = "selected" """ or "",
            # bpr.bpB.displayName())) for bpr in BPRelation.objects.filter(relation__exact='A1')])
            salesman = GetEmployeeOfDepartment('SD')
            options = ''.join([('<option value="%s" %s>%s</option>' % (
            bp.id, bool(str(bp.id) == str(self.value)) and """ selected = "selected" """ or "",
            bp.displayName())) for bp in salesman])
        if self.fieldType == 'bpRelation':
            options = ''.join([('<option value="%s" %s>%s</option>' % (
                t.key, bool(str(t.key) == str(self.value)) and """ selected = "selected" """ or "", t.description)) for
                               t in
                               BPRelType.objects.all()])
        if self.fieldType == 'travelAmountRange':
            range = [
                {'key': '1', 'value': '1-50'},
                {'key': '2', 'value': '50-100'},
                {'key': '3', 'value': '100-500'},
                {'key': '4', 'value': '500+'},
            ]
            options = ''.join([('<option value="%s" %s>%s</option>' % (
                t['key'], bool(t['key'] == self.value) and """ selected = "selected" """ or "", t['value'])) for t in
                               range])
        if self.nullable:
            options = '<option value="all">All</option>%s' % options
        output = """
<select class="form-control" id="%s" name="%s" data-rel="chosen">
	%s
</select>

""" % (self.name, self.name, options)
        return output


@register.tag(name='FieldSelectTag')
def fieldSelectTag(parse, token):
    try:
        length = len(token.split_contents())
        if length == 6:
            tag_name, name, value, orderType, fieldType, extKey = token.split_contents()
            value = parse.compile_filter(value)
            tag = FieldSelectTag()
            tag.name = name.strip('"')
            tag.value = value
            tag.orderType = orderType.strip('"')
            tag.fieldType = fieldType.strip('"')
            tag.extKey = extKey.strip('"')
            tag.nullable = None
            return tag
        elif length == 7:
            tag_name, name, value, orderType, fieldType, extKey, nullable = token.split_contents()
            value = parse.compile_filter(value)
            tag = FieldSelectTag()
            tag.name = name.strip('"')
            tag.value = value
            tag.orderType = orderType.strip('"')
            tag.fieldType = fieldType.strip('"')
            tag.extKey = extKey.strip('"')
            tag.nullable = nullable
            return tag
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly 5 arguments: name, value, orderType, fieldType, and extKey" % \
            token.split_contents[0]
    return FieldSelectTag()
