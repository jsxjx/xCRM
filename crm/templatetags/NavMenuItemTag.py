from django import template

register = template.Library()


class NavMenuItemTag(template.Node):
    def __init__(self, nodeList, pageApp, pageParams):
        #    def __init__(self, nodeList,**kwargs):
        self.nodeList = nodeList
        self.pageApp = pageApp.strip('"')
        # self.pageAction = pageAction.strip('"')
        self.pageParams = pageParams.strip('"')

    #    self.pageMode = pageMode.strip('"')
    def render(self, context):
        active = ""
        nav = context.get('nav', None)
        if nav and self.pageApp == nav['pageApp']:
            active = """ class="active" """
        innerContent = self.nodeList.render(context)
        output = """<li %s><a class="ajax-link" href="###" onclick="toNav('%s','','%s','')">%s</a></li>""" % (
        active, self.pageApp, self.pageParams, innerContent)
        return output


@register.tag(name='NavMenuItemTag')
def navMenuItemTag(parse, token):
    nodeList = parse.parse(('EndNavMenuItemTag',))
    parse.delete_first_token()
    try:
        tag_name, pa, pp = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly 3 arguments: app, params and mode" \
            % token.split_contents
    return NavMenuItemTag(nodeList, pa, pp)
