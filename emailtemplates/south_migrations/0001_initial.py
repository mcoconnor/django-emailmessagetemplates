# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailMessageTemplate'
        db.create_table(u'emailtemplates_emailmessagetemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('subject_template', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('body_template', self.gf('django.db.models.fields.TextField')()),
            ('sender', self.gf('django.db.models.fields.EmailField')(default='', max_length=75, blank=True)),
            ('base_cc', self.gf('emailtemplates.fields.SeparatedValuesField')(default='', blank=True)),
            ('base_bcc', self.gf('emailtemplates.fields.SeparatedValuesField')(default='', blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('edited_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('edited_user', self.gf('django.db.models.fields.TextField')(max_length=30, blank=True)),
        ))
        db.send_create_signal(u'emailtemplates', ['EmailMessageTemplate'])

        # Adding unique constraint on 'EmailMessageTemplate', fields ['name', 'content_type', 'object_id']
        db.create_unique(u'emailtemplates_emailmessagetemplate', ['name', 'content_type_id', 'object_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'EmailMessageTemplate', fields ['name', 'content_type', 'object_id']
        db.delete_unique(u'emailtemplates_emailmessagetemplate', ['name', 'content_type_id', 'object_id'])

        # Deleting model 'EmailMessageTemplate'
        db.delete_table(u'emailtemplates_emailmessagetemplate')


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
            'base_bcc': ('emailtemplates.fields.SeparatedValuesField', [], {'default': "''", 'blank': 'True'}),
            'base_cc': ('emailtemplates.fields.SeparatedValuesField', [], {'default': "''", 'blank': 'True'}),
            'body_template': ('django.db.models.fields.TextField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'edited_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'edited_user': ('django.db.models.fields.TextField', [], {'max_length': '30', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'subject_template': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        }
    }

    complete_apps = ['emailtemplates']