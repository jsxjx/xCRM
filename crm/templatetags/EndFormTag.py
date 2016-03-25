from django import template

register = template.Library()


class EndFormTag(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        output = "</form>"
        return output


@register.tag(name='EndFormTag')
def endFormTag(parse, token):
    try:
        tag_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly two arguments: path and text" % \
            token.split_contents[0]
    return EndFormTag()
