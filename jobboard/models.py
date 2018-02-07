from django.db import models
from tagging.fields import TagField
from django.conf import settings as dsettings
from django.utils.translation import get_language
from django.db.models.signals import post_save
from conference.models import postSaveResizeImageHandler
import os


def _fs_upload_to(subdir, attr=None, package='conference'):
    if attr is None:
        attr = lambda i: i.slug

    def wrapper(instance, filename):
        fpath = os.path.join(package, subdir, '%s%s' % (attr(instance), os.path.splitext(filename)[1].lower()))
        ipath = os.path.join(dsettings.MEDIA_ROOT, fpath)
        if os.path.exists(ipath):
            os.unlink(ipath)
        return fpath
    return wrapper


class JobOffer(models.Model):
    """
        Offerta di lavoro da parte di una azienda. Il modello comprende logo
        tags, descrizione e titolo
    """
    job_title_it = models.CharField(max_length=250, help_text='nome posizione - tipo di lavoro (IT)')
    job_title_en = models.CharField(max_length=250, help_text='nome posizione - tipo di lavoro (EN)')
    slug = models.SlugField()
    company = models.CharField(max_length=100, help_text='nome azienda')
    logo = models.ImageField(
        upload_to=_fs_upload_to('job'), blank=True,
        help_text='Inserire un immagine raster sufficientemente grande da poter essere scalata al bisogno'
    )
    job_description_it = models.TextField(default='')
    job_description_en = models.TextField(default='')
    url = models.URLField(blank=True, help_text='Sito web azienda')
    tags = TagField()

    @property
    def job_title(self):
        language = get_language()
        return getattr(self, 'job_title_%s' % language, '')

    @property
    def job_description(self):
        language = get_language()
        return getattr(self, 'job_description_%s' % language, '')

    class Meta:
        ordering = ['company']

    def __unicode__(self):
        return self.company


post_save.connect(postSaveResizeImageHandler, sender=JobOffer)
