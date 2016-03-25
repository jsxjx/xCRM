from django import template
from crm.models import UserLogin
from crm.common import *

register = template.Library()


class AuthRequireTag(template.Node):
    def __init__(self, nodeList, name, value, value2):
        self.nodeList = nodeList
        self.name = name.strip('"')
        self.value = value.strip('"')
        self.value2 = value2.strip('"')

    def render(self, context):
        # innerContent = self.nodeList.render(context)
        output = ""
        p = {}
        p['name'] = self.name
        p['value'] = self.value
        p['value2'] = self.value2
        authPass = checkAuthObject(context, **p)
        if authPass:
            innerContent = self.nodeList.render(context)
            return innerContent
        else:
            return output


@register.tag(name='AuthRequireTag')
def authRequireTag(parse, token):
    nodeList = parse.parse(('EndAuthRequireTag',))
    parse.delete_first_token()
    try:
        tag_name, name, value, value2 = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly 3 arguments: path and text" % \
            token.split_contents[0]
    return AuthRequireTag(nodeList, name, value, value2)
