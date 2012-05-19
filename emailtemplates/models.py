from django.db import models
from django.core.mail import EmailMessage
from django.core.validators import email_re
from django.template.loader import render_to_string
from django.template import Context, Template
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from fields import SeparatedValuesField
from app_settings import AppSettings

class EmailTemplateError(ValueError):
    pass

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
            return self.get(name=name,object_id=object_id, 
                            content_type=content_type, enabled=True)
        except EmailMessageTemplate.DoesNotExist:
            if not related_object:
                raise
            return self.get(name=name, object_id=None, content_type=None, 
                            enabled=True)
        

class EmailMessageTemplate(models.Model,EmailMessage):
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
    subject_template = models.CharField(max_length=2000)
    body_template = models.TextField()
    sender = models.EmailField(max_length=75, blank=True, default='', verbose_name="'From' Email", help_text="The address this email should appear to be sent 'from'.  If blank, defaults to '{0}'.".format(AppSettings.EMAILTEMPLATES_DEFAULT_FROM_EMAIL))
    base_cc = SeparatedValuesField(max_length=200, blank=True, default='', verbose_name="CC", help_text="An optional list of email addresses to be CCed when this template is sent (in addition to any addresses specified when the message is sent)")
    base_bcc = SeparatedValuesField(max_length=200, blank=True, default='', verbose_name="BCC", help_text="An optional list of email addresses to be BCCed when this template is sent (in addition to any addresses specified when the message is sent)")
    
    #Other information
    description = models.TextField()
    enabled = models.BooleanField(default=True,help_text="When unchecked, this email will not be sent.")
    suppress_log = models.BooleanField(default=False,help_text="When checked, a log entry will not be generated when this email is sent, regardless of the EMAILTEMPLATES_LOG_EMAILS setting, which is currently '{0}'. Can be used for frequently sent, low value messages.".format(AppSettings.EMAILTEMPLATES_LOG_EMAILS))
    edited_date = models.DateTimeField(auto_now=True,editable=False,blank=True)
    edited_user = models.TextField(max_length=30,editable=False,blank=True) 
    
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
    def to(self,value):
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
    def cc(self,value):
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
        return list(set(self._instance_bcc) | set(self.base_bcc if self.base_ccb is not None else []))
    
    @bcc.setter
    def bcc(self,value):
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
        return self._instance_from or self.sender or \
            AppSettings.EMAILTEMPLATES_DEFAULT_FROM_EMAIL
    
    @from_email.setter
    def from_email(self,value):
        """
        No-op to prevent EmailMessage from ignoring the configured defaults 
        """
        return
            
    def __unicode__(self):
        status = " (Disabled)" if not self.enabled else ""
        if self.related_object:
            return "{0} for {1}{2}".format(self.name,self.related_object,status)
        return self.name + status

    # Preparing and sending messages   
    _prepared = False
    _errors = []
    
    def _render_subject(self,context):
        try:
            return subject_prefix + Template(self.subject_template).render(c)
        except  Exception as e:
            self._errors.append("Failed to render subject: ({0})".format(e))
        return ""

    def _render_body(self,context):
        try:
            return Template(self.body_template).render(c)
        except Exception as e:
            self._errors.append("Failed to render body: ({0})".format(e))
        return ""

    def prepare(self, context={}, from_email=None, to=[], cc=[], bcc=[], 
                connection=None, attachments=None, headers={}, 
                subject_prefix=""):
        """
        Initialize a single email message and render the subject and body 
        using a supplied context.
        """
        
        #Set up the EmailMessage
        if from_email:
            self._instance_from = from_email
        if to:
            assert not isinstance(to, basestring), '"to" argument must be a list or tuple'
            self.to = to   
        if cc:
            assert not isinstance(cc, basestring), '"cc" argument must be a list or tuple'
            self.cc = cc
        if bcc:
            assert not isinstance(bcc, basestring), '"bcc" argument must be a list or tuple'
            self.bcc = bcc
            
        self.attachments = attachments or []
        self.extra_headers = headers or {}
        self.connection = connection
        
        #Render the templates
        c = Context(context)
        self.subject = self._render_subject(c)
        self.body = self._render_body(c) 
           
        self._prepared = True
        
                
    def send(self, fail_silently=False):
        """
        Sends the email message.
        """
        
        assert self._prepared, 'The EmailMessageTemplate must be prepared before sending.'
        
        #If there weren't problems preparing the message, try to send it
        result = None
        send_error = None
        if not len(self._errors):
            try:
                result = super(EmailMessageTemplate,self).send(fail_silently=False)
            except Exception as send_error:
                self._errors.append("Sending email failed: {0}".format(send_err))
        
        #Log the results
        if AppSettings.EMAILTEMPLATES_LOG_EMAILS and not self.suppress_log:
            log = Log(template=self,
                      recipients=self.recipients(),
                      status=Log.STATUS.FAILURE if len(self._errors) else Log.STATUS.SUCCESS,
                      message='\n'.join(self._errors))
            log.save()
            
        #Raise an exception if the user has requested it
        if not fail_silently:
            if send_error:
                raise send_error
            if len(self._errors):
                raise EmailTemplateError(', '.join(self._errors))
            
        return result
        
    class Meta:
        ordering = ('name',)
        unique_together = (("name", "content_type", "object_id"),)
        verbose_name="Email Template"
    
class Log(models.Model):
    """
    The record of one attempt to send a templated email message.
    """

    class STATUS:
        SUCCESS = 'S'
        FAILURE = 'F'
        
    STATUS_CHOICES = (
                        (STATUS.SUCCESS,'SUCCESS. Message sent.',),
                        (STATUS.FAILURE,'FAILURE. Message not sent due to errors.',),
                    )
    
    template = models.ForeignKey(EmailMessageTemplate)
    recipients = models.TextField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True) 
    
    def __unicode__(self):
        return "  {0} '{1}' at {2}.".format(self.get_status_display(),self.template,self.date,)
