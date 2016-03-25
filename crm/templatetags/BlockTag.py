from django import template
from crm.common import *

register = template.Library()


class BlockTag(template.Node):
    def render(self, context):
        s = ""
        m = ""
        c = ""
        if self.title != None:
            title = parseFilter(self.title, context)
        else:
            phraseText = getPhrase(context['request'], self.appid, self.pid)
            title = phraseText
        if self.hasSetting == 'Y':
            s = """
<a href="#" class="btn btn-setting btn-round btn-default"><i
                            class="glyphicon glyphicon-cog"></i></a>
"""
        if self.hasMin == 'Y':
            m = """
<a href="#" class="btn btn-minimize btn-round btn-default"><i
                            class="glyphicon glyphicon-chevron-up"></i></a>
"""
        if self.hasClose == 'Y':
            c = """
<a href="#" class="btn btn-close btn-round btn-default"><i
                            class="glyphicon glyphicon-remove"></i></a>
"""
        innerContent = self.nodeList.render(context)
        output = """
          <div class="box-inner">
            <div class="box-header well">
                <h2><i class="glyphicon glyphicon-list-alt"></i> %s</h2>

                <div class="box-icon">
                   %s %s %s 
                </div>
            </div>
            <div class="box-content">
                %s
            </div>
          </div>

""" % (title, s, m, c, innerContent)
        return output


@register.tag(name='BlockTag')
def blcokTag(parse, token):
    nodeList = parse.parse(('EndBlockTag',))
    parse.delete_first_token()
    try:
        length = len(token.split_contents())
        if length == 5:
            # log.info('5')
            tag_name, title, s, m, c = token.split_contents()
            # log.info('%s %s %s %s' % (title,s,m,c))
            title = parse.compile_filter(title)
            tag = BlockTag()
            tag.nodeList = nodeList
            tag.title = title
            # tag.title = parse.compile_filter(tag.title)
            tag.hasSetting = s
            tag.hasMin = m
            tag.hasClose = c
            return tag
            # return BlockTag(nodeList,title,s,m,c)
        elif length == 6:
            # log.info('6')
            tag_name, appid, pid, s, m, c = token.split_contents()
            tag = BlockTag()
            tag.nodeList = nodeList
            tag.title = None
            tag.pid = pid
            tag.appid = appid
            tag.hasSetting = s
            tag.hasMin = m
            tag.hasClose = c
            return tag
    # return BlockTag(noeList,pid,appid,s,m,c)
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly 4 arguments: path and text" % \
            token.split_contents[0]
    return BlockTag()
