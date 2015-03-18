from email.utils import getaddresses, formataddr

from django import forms
from django.utils.translation import ugettext_lazy as _


class EmailListField(forms.CharField):
    """
    A Django form field which validates a list of email addresses.
    Adapted from http://djangosnippets.org/snippets/1677/
    """
    default_error_messages = {
        'invalid': _('Please enter a valid list of e-mail addresses.')
    }

    def prepare_value(self, value):
        if isinstance(value, list) or isinstance(value, tuple):
            return ', '.join(value)
        return value
        
    def clean(self, value):
        value = super(EmailListField, self).clean(value)

        field = forms.EmailField()

        try:
            return [
                formataddr((name, field.clean(addr)))
            for name, addr in getaddresses([value])]
        except forms.ValidationError:
            raise forms.ValidationError(self.error_messages['invalid'])
