from django import template
from crm.models import UserLogin
from crm.common import *

register = template.Library()


class AssignmentBlockTag(template.Node):
    def __init__(self, nodeList, contextname, assignmentblockname):
        self.nodeList = nodeList
        self.contextname = contextname.strip('"')
        self.assignmentblockname = assignmentblockname.strip('"')


    def render(self, context):
        output = ""
        custContext = getContext(context['request'], self.contextname)
        if hasattr(custContext, 'orderType'):
            value = eval('custContext.orderType')
            ot = OrderType.objects.get(key=value)
            if ot.assignmentBlock is not None:
                assignmentBlocks = ot.assignmentBlock.split(',')
                if self.assignmentblockname in assignmentBlocks:
                    innerContent = self.nodeList.render(context)
                    return innerContent
        elif hasattr(custContext, 'bpType'):
            value = eval('custContext.bpType')
            bt = BPType.objects.get(key=value)
            if bt.assignmentBlock is not None:
                assignmentBlocks = bt.assignmentBlock.split(',')
                if self.assignmentblockname in assignmentBlocks:
                    innerContent = self.nodeList.render(context)
                    return innerContent
        return output


@register.tag(name='AssignmentBlockTag')
def assignmentBlockTag(parse, token):
    nodeList = parse.parse(('EndAssignmentBlockTag',))
    parse.delete_first_token()
    try:
        tag_name, contextname, assignmentblockname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly 3 arguments: path and text" % \
            token.split_contents[0]
    return AssignmentBlockTag(nodeList, contextname, assignmentblockname)
