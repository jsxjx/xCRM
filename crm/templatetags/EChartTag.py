from django import template
from crm.models import SitePhrase
from crm.common import *

register = template.Library()


class EChartTag(template.Node):
    def __init__(self, name, height, options):
        self.name = name.strip('"')
        self.height = height.strip('"')
        self.options = options

    def render(self, context):
        name = '%s%d%d' % (self.name, int(time.time()), randint(0, 999999))
        options = parseFilter(self.options, context)
        javascript = """<script>var echart_%s = echarts.init(document.getElementById('%s'),'macarons'); var option = %s;echart_%s.setOption(option);</script>""" % (
        name, name, options, name)
        html = """<div id="%s" style="height:%s;"></div>""" % (name, self.height)
        html = '%s%s' % (html, javascript)
        return html


@register.tag(name='EChartTag')
def eChartTag(parse, token):
    try:
        tag_name, name, height, options = token.split_contents()
        options = parse.compile_filter(options)
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly 3 arguments: name, height and options" % \
            token.split_contents[0]
    return EChartTag(name, height, options)
