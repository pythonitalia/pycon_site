# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import MarkitUpPluginModel, SlideControl


class MarkItUpPlugin(CMSPluginBase):
    name = _(u'MarkItUp')
    model = MarkitUpPluginModel
    render_template = 'djangocms_markitup/markitup.html'

plugin_pool.register_plugin(MarkItUpPlugin)

class AlmaSlider(CMSPluginBase):
    name = _(u"Slideshow slick")
    allow_children = True
    model = SlideControl
    render_template = "slickslider/slider_plugin.html"

plugin_pool.register_plugin(AlmaSlider)
