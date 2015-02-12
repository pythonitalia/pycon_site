# -*- coding: utf-8 -*-
from .models import MarkitUpPluginModel
from django.template import Template
from django.utils.safestring import mark_safe
from markitup.fields import render_func

def process_templatetags(instance, placeholder, rendered_content, original_context):
    """
    This plugin processor render the resulting content to parse for templatetags
    in the plugin output
    """
    def render(tpl_source):
        try:
            template = Template(tpl_source)
        except Exception, e:
            return u'<p><strong>Template Error: {}</strong></p>{}'.format(str(e), rendered_content)
        return template.render(original_context)

    if isinstance(instance, MarkitUpPluginModel):
        # this is a markitup field, rendered_content is not anymore a valid
        # django template. I have to work on the raw content.
        mark = render(instance.body.raw)
        html = mark_safe(render_func(mark))
    else:
        html = render(rendered_content)
    return html
