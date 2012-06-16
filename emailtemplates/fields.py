from django.db import models
from django.core.exceptions import ValidationError
from django.template import Context, Template, TemplateSyntaxError


class SeparatedValuesField(models.TextField):
    """
    Adapted from http://justcramer.com/2008/08/08/custom-fields-in-django/
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(SeparatedValuesField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return
        if isinstance(value, list):
            return value
        return value.split(self.token)

    def get_prep_value(self, value):
        if not value:
            return ''
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([unicode(s) for s in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return ",".join(value)


def validate_template_syntax(value):
    """
    Ensure that there aren't any gross errors in a template string
    """
    print 'hello'
    try:
        print Template(value).render(Context({}))
    except TemplateSyntaxError, e:
        raise ValidationError("Invalid Template: " + e.message)
