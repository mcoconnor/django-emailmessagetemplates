from django.conf import settings
from django.contrib import admin
from django import forms

from models import EmailMessageTemplate
from forms import EmailListField


class EmailMessageTemplateAdmin(admin.ModelAdmin):
    readonly_fields = ('related_item_display',)
    
    def __init__(self, *args, **kwargs):
        super(EmailMessageTemplateAdmin, self).__init__(*args, **kwargs)
        self.exclude = ['content_type', 'object_id']
        if not settings.EMAILMESSAGETEMPLATES_ALLOW_HTML_MESSAGES:
            self.exclude.extend(['type','autogenerate_text','body_template_html']) 

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['base_cc', 'base_bcc',]:
            request = kwargs.pop("request", None)
            return db_field.formfield(form_class=EmailListField, **kwargs)
        return super(EmailMessageTemplateAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    class Media:
        js = (
            'emailmessagetemplates/js/admin.js',
            )
    
admin.site.register(EmailMessageTemplate, EmailMessageTemplateAdmin)
