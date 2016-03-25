from django import template
from crm.models import SiteMenuItem, SitePhrase

register = template.Library()


class MenuTag(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        lan = context.get('lan', 'en')
        up = context.get('up', None)
        filter = {}
        filter['parentMenuId'] = None
        filter['valid'] = True
        if up:
            filter['role__exact'] = up.get('loginRole', None)
        menus = SiteMenuItem.objects.filter(**filter).order_by("sortOrder")
        itemHtml = []
        for m in menus:
            phraseId = m.phraseId
            appId = m.appId
            pageApp = m.pageApp
            phrase = SitePhrase.objects.filter(app__appId=appId, phraseId=phraseId, phraseLan__key=lan)
            phraseText = "[%s %s %s]" % (appId, phraseId, lan)
            if phrase:
                phraseText = phrase[0].content
            active = ""
            nav = context.get('nav', None)
            if nav and pageApp == nav['pageApp']:
                active = """ active """
            submenus = SiteMenuItem.objects.filter(parentMenuId=m.id, valid=True)
            if submenus:
                subHtml = ''
                for submenu in submenus:
                    phraseId = submenu.phraseId
                    appId = submenu.appId
                    pageApp = submenu.pageApp
                    phrase = SitePhrase.objects.filter(app__appId=appId, phraseId=phraseId, phraseLan__key=lan)
                    phraseText = "[%s %s %s]" % (appId, phraseId, lan)
                    if phrase:
                        phraseText = phrase[0].content
                    active = ""
                    nav = context.get('nav', None)
                    if nav and pageApp == nav['pageApp']:
                        active = """ active """
                    sub = """<li class="%s"><a class="ajax-link" href="#" onclick="toNav('%s')">%s</a></li>""" % (
                        active, pageApp, phraseText)
                    subHtml = ''.join([subHtml, sub])
                subItems = """<ul class="nav nav-pills nav-stacked">%s</ul>""" % subHtml
                item = """<li class="accordion %s"><a href="#"">%s</a>%s</li>""" % (
                    active, phraseText, subItems)
            else:
                item = """<li class="%s"><a class="ajax-link" href="#" onclick="toNav('%s')">%s</a></li>""" % (
                    active, pageApp, phraseText)
            itemHtml.append(item)
        menu = """<div class="sidebar-nav" id="nav">
  <div class="nav-canvas">
    <div class="nav-sm nav nav-stacked"></div>
    <ul class="nav nav-pills nav-stacked main-menu">
    %s         
    </ul>
  </div>
</div>""" % (''.join(itemHtml))
        return menu


@register.tag(name='MenuTag')
def menuTag(parse, token):
    try:
        tag_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires no arguments" % \
            token.split_contents[0]
    return MenuTag()
