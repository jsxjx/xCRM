from django import template

register = template.Library()


class NavMenuTag(template.Node):
    def __init__(self, nodeList, nav_name):
        self.nodeList = nodeList
        self.name = nav_name.strip('"')

    def render(self, context):
        innerContent = self.nodeList.render(context)
        output = """
              <div class="sidebar-nav" id="%s">
                <div class="nav-canvas">
                  <div class="nav-sm nav nav-stacked">
                  </div>
                  <ul class="nav nav-pills nav-stacked main-menu">
                    %s 
                  </ul>
                </div>
              </div>
""" % (self.name, innerContent)
        return output


@register.tag(name='NavMenuTag')
def navMenuTag(parse, token):
    nodeList = parse.parse(('EndNavMenuTag',))
    parse.delete_first_token()
    try:
        tag_name, nav_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly 1 argument: path and text" % \
            token.split_contents[0]
    return NavMenuTag(nodeList, nav_name)
