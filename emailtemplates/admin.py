from django.contrib import admin
from django import forms

from models import EmailMessageTemplate
from forms import EmailListField


class EmailMessageTemplateAdmin(admin.ModelAdmin):
    readonly_fields = ('description', 'content_type', 'object_id',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['base_cc', 'base_bcc',]:
            request = kwargs.pop("request", None)
            return db_field.formfield(form_class=EmailListField, **kwargs)
        return super(EmailMessageTemplateAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
admin.site.register(EmailMessageTemplate, EmailMessageTemplateAdmin)
