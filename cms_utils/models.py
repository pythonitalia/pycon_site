# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from markitup.fields import MarkupField
from cms.models import CMSPlugin


class MarkitUpPluginModel(CMSPlugin):
    body = MarkupField()

class SlideControl(CMSPlugin):
    fade = models.BooleanField(_(u'Fade effect'), default=False)
    automatic = models.BooleanField(_(u'Autostart'), default=False)
    timeout = models.PositiveSmallIntegerField(_(u'Slide time'), default=3000,
                                               help_text=_(u'In milliseconds'))
    arrows = models.BooleanField(_(u'Arrows'), default=False)
    border = models.BooleanField(_(u'Border'), default=True)

    def __unicode__(self):
        return u"slick slider - auto %s - fade %s" % (self.fade, self.automatic)

    class Meta:
        verbose_name = _("slick slider")
        verbose_name_plural = _("slick sliders")