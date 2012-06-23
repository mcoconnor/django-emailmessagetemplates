from django.db import models
from django.core.mail import EmailMessage
from django.template import Context, Template
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from fields import SeparatedValuesField, validate_template_syntax
from app_settings import AppSettings


class EmailMessageTemplateManager(models.Manager):

    def get_template(self, name, related_object=None):
        """
        If a related object is specified, we'll first try to retrieve a template 
        that matches both the name and the object, and if none exists, we'll try 
        to retrieve a template with the specified name without a related object 
        instead (to support situations where some objects have a specialized 
        template, but, when none exists, we want to fall back to a default). 
        """
        if related_object:
            object_id = related_object.pk
            content_type = ContentType.objects.get_for_model(related_object)
        else:
            object_id = None
            content_type = None

        try:
            return self.get(name=name, object_id=object_id,
                            content_type=content_type, enabled=True)
        except EmailMessageTemplate.DoesNotExist:
            if not related_object:
                raise
            return self.get(name=name, object_id=None, content_type=None,
                            enabled=True)


class EmailMessageTemplate(models.Model, EmailMessage):
    """
    A template for an email to be sent by the system.  Also a subclass of 
    Django's EmailMessage, so its methods can be used for sending.
    """

    #Fields to identify a template
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, verbose_name="Related Object Type")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="Related Object ID")
    related_object = generic.GenericForeignKey('content_type', 'object_id')

    #Fields to override from EmailMessage
    subject_template = models.CharField(max_length=2000, validators=[validate_template_syntax])
    body_template = models.TextField(validators=[validate_template_syntax])
    sender = models.EmailField(max_length=75, blank=True, default='', verbose_name="'From' Email", help_text="The address this email should appear to be sent 'from'.  If blank, defaults to '{0}'.".format(AppSettings.EMAILTEMPLATES_DEFAULT_FROM_EMAIL))
    base_cc = SeparatedValuesField(blank=True, default='', verbose_name="CC", help_text="An optional list of email addresses to be CCed when this template is sent (in addition to any addresses specified when the message is sent)")
    base_bcc = SeparatedValuesField(blank=True, default='', verbose_name="BCC", help_text="An optional list of email addresses to be BCCed when this template is sent (in addition to any addresses specified when the message is sent)")

    #Other information
    description = models.TextField()
    enabled = models.BooleanField(default=True, help_text="When unchecked, this email will not be sent.")
    suppress_log = models.BooleanField(default=False, help_text="When checked, a log entry will not be generated when this email is sent, regardless of the EMAILTEMPLATES_LOG_EMAILS setting, which is currently '{0}'. Can be used for frequently sent, low value messages.".format(AppSettings.EMAILTEMPLATES_LOG_EMAILS))
    edited_date = models.DateTimeField(auto_now=True, editable=False, blank=True)
    edited_user = models.TextField(max_length=30, editable=False, blank=True)

    objects = EmailMessageTemplateManager()

    #Ensure compatibility with EmailMessage CC, BCC, and from_email data
    _instance_to = []
    _instance_cc = []
    _instance_bcc = []
    _instance_from = None

    @property
    def to(self):
        """
        The recipient addresses specified on the instance.
        """
        return self._instance_to

    @to.setter
    def to(self, value):
        """
        Set the recipient addresses on the instance.
        """
        self._instance_to = value

    @property
    def cc(self):
        """
        The unique set of CC addresses specified either in the template or on 
        the instance.
        """
        return list(set(self._instance_cc) | set(self.base_cc if self.base_cc is not None else []))

    @cc.setter
    def cc(self, value):
        """
        Add any addresses not in the template's CC list to the instance list.
        """
        self._instance_cc = list(set(value) - set(self.base_cc if self.base_cc is not None else []))

    @property
    def bcc(self):
        """
        The unique set of BCC addresses specified either in the template or on 
        the instance.
        """
        return list(set(self._instance_bcc) | set(self.base_bcc if self.base_bcc is not None else []))

    @bcc.setter
    def bcc(self, value):
        """
        Add any addresses not in the template's BCC list to the instance list.
        """
        self._instance_bcc = list(set(value) - set(self.base_cc if self.base_bcc is not None else []))

    @property
    def from_email(self):
        """
        Use the specified sender if set, and then fall back to the template 
        sender, and finally the setting value.
        """
        return self._instance_from or self.sender or\
            AppSettings.EMAILTEMPLATES_DEFAULT_FROM_EMAIL

    @from_email.setter
    def from_email(self, value):
        """
        Set the sender addresses on the instance.
        """
        self._instance_from = value

    def __unicode__(self):
        status = " (Disabled)" if not self.enabled else ""
        if self.related_object:
            return "{0} for {1}{2}".format(self.name, self.related_object, status)
        return self.name + status

    # Preparing and sending messages
    _context = Context({})
    subject_prefix = ""

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        if issubclass(type(value), Context):
            self._context = value
        else:
            self._context = Context(value)

    @property
    def subject(self):
        return self.subject_prefix + Template(self.subject_template).render(self.context)

    @subject.setter
    def subject(self, value):
        """
        No-op to prevent EmailMessage from stomping on the template 
        """
        pass

    @property
    def body(self):
        return Template(self.body_template).render(self.context)

    @body.setter
    def body(self, value):
        """
        No-op to prevent EmailMessage from stomping on the template 
        """
        pass
                        
    def send(self, fail_silently=False):
        """
        Sends the email message.
        """
        result = None
        send_error = None
        try:
            result = super(EmailMessageTemplate, self).send(fail_silently=False)
        except Exception as e:
            send_error = e

        #Log the results
        if AppSettings.EMAILTEMPLATES_LOG_EMAILS and not self.suppress_log:
            message = None
            if send_error:
                message = send_error.message if len(send_error.message) <= 100 else (send_error.message[:97] + '...')

            log = Log(template=self,
                      recipients=self.recipients(),
                      status=Log.STATUS.FAILURE if send_error else Log.STATUS.SUCCESS,
                      message=message).save()

        #Raise an exception if the user has requested it
        if not fail_silently and send_error:
            raise send_error

        return result

    def __init__(self,*args,**kwargs):
        """
        Initialize the template, ensuring that the from_email is not set 
        unnecessarly
        """
        super(EmailMessageTemplate, self).__init__(*args,**kwargs)
        #resetting sender to default so EmailMessage won't stomp on it
        self.from_email = None
        

    class Meta:
        ordering = ('name',)
        unique_together = (("name", "content_type", "object_id"),)
        verbose_name = "Email Template"


class Log(models.Model):
    """
    The record of one attempt to send a templated email message.
    """

    class STATUS:
        SUCCESS = 'S'
        FAILURE = 'F'

    STATUS_CHOICES = (
                        (STATUS.SUCCESS, 'SUCCESS. Message sent.',),
                        (STATUS.FAILURE, 'FAILURE. Message not sent due to errors.',),
                    )

    template = models.ForeignKey(EmailMessageTemplate)
    recipients = SeparatedValuesField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    message = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "  {0} '{1}' at {2}.".format(self.get_status_display(), self.template, self.date,)
