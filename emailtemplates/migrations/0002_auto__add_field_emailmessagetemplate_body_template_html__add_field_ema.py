# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'EmailMessageTemplate.body_template_html'
        db.add_column(u'emailtemplates_emailmessagetemplate', 'body_template_html',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'EmailMessageTemplate.type'
        db.add_column(u'emailtemplates_emailmessagetemplate', 'type',
                      self.gf('django.db.models.fields.CharField')(default='text/plain', max_length=20),
                      keep_default=False)

        # Adding field 'EmailMessageTemplate.autogenerate_text'
        db.add_column(u'emailtemplates_emailmessagetemplate', 'autogenerate_text',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'EmailMessageTemplate.body_template_html'
        db.delete_column(u'emailtemplates_emailmessagetemplate', 'body_template_html')

        # Deleting field 'EmailMessageTemplate.type'
        db.delete_column(u'emailtemplates_emailmessagetemplate', 'type')

        # Deleting field 'EmailMessageTemplate.autogenerate_text'
        db.delete_column(u'emailtemplates_emailmessagetemplate', 'autogenerate_text')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'emailtemplates.emailmessagetemplate': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('name', 'content_type', 'object_id'),)", 'object_name': 'EmailMessageTemplate'},
            'autogenerate_text': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'base_bcc': ('emailtemplates.fields.SeparatedValuesField', [], {'default': "''", 'blank': 'True'}),
            'base_cc': ('emailtemplates.fields.SeparatedValuesField', [], {'default': "''", 'blank': 'True'}),
            'body_template': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'body_template_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'edited_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'edited_user': ('django.db.models.fields.TextField', [], {'max_length': '30', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'subject_template': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'text/plain'", 'max_length': '20'})
        }
    }

    complete_apps = ['emailtemplates']