from django import template

register = template.Library()


class FormTag(template.Node):
    def __init__(self, nodeList, form_name, form_action):
        self.nodeList = nodeList
        self.name = form_name.strip('"')
        self.action = form_action.strip('"')

    def render(self, context):
        innerContent = self.nodeList.render(context)
        output = """
<form name="%s" action="%s" method="POST">
<input id="navForm_pageApp" type="hidden" name="pageApp" value="home">
<input id="navForm_pageAction" type="hidden" name="pageAction" value="home">
<input id="navForm_pageParams" type="hidden" name="pageParams" value="">
<input id="navForm_pageMode" type="hidden" name="pageMode" value="display">
%s
</form>""" % (self.name, self.action, innerContent)
        return output


@register.tag(name='FormTag')
def formTag(parse, token):
    nodeList = parse.parse(('EndFormTag',))
    parse.delete_first_token()
    try:
        tag_name, form_name, form_action = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly 2 arguments: path and text" % \
            token.split_contents[0]
    return FormTag(nodeList, form_name, form_action)
