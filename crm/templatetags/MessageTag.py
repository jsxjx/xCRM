from django import template
from crm.models import SitePhrase

register = template.Library()


class MessageTag(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        messages = context.get('messagebar', None)
        if not messages:
            return ""
        htmls = []
        for message in messages:
            t = 'info'
            if message['type'] == 'error':
                t = 'danger'
            elif message['type'] == 'success':
                t = 'success'
            html = """<div class="alert alert-%s"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>%s</strong></div>""" % (
            t, message['content'])
            htmls.append(html)
        return ''.join(["<div class='row'><div class='col-md-12'>", ''.join(htmls), "</div></div>"])


@register.tag(name='MessageTag')
def messageTag(parse, token):
    try:
        tag_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires no arguments" % \
            token.split_contents[0]
    return MessageTag()
