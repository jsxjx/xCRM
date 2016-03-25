from django import template
from crm.models import SitePhrase
from crm.common import *

register = template.Library()


class PhraseTag(template.Node):
    def __init__(self, appId, phraseId):
        self.appId = appId
        self.phraseId = phraseId

    def render(self, context):
        appId = parseFilter(self.appId, context)
        phraseId = parseFilter(self.phraseId, context)
        return getPhrase(context['request'], appId, phraseId)


@register.tag(name='PhraseTag')
def phraseTag(parse, token):
    # log.info('phrase tag initialized')
    try:
        tag_name, appId, phraseId = token.split_contents()
        # log.info('tag: %s %s' % (appId,phraseId))
        appId = parse.compile_filter(appId)
        phraseId = parse.compile_filter(phraseId)
        # log.info('compile:%s %s' % (phraseId,type(phraseId)))
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly 2 arguments: appId and phraseId" % \
            token.split_contents[0]
    return PhraseTag(appId, phraseId)
