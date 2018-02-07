# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'JobOffer'
        db.create_table(u'jobboard_joboffer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('job_title_it', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('job_title_en', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('job_description_it', self.gf('django.db.models.fields.TextField')(default='')),
            ('job_description_en', self.gf('django.db.models.fields.TextField')(default='')),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
        ))
        db.send_create_signal(u'jobboard', ['JobOffer'])


    def backwards(self, orm):
        # Deleting model 'JobOffer'
        db.delete_table(u'jobboard_joboffer')


    models = {
        u'jobboard.joboffer': {
            'Meta': {'ordering': "['company']", 'object_name': 'JobOffer'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_description_en': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'job_description_it': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'job_title_en': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'job_title_it': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['jobboard']