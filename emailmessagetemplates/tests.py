from datetime import datetime, timedelta

from django.core.management import call_command
from django.core import mail
from django.test import TestCase
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.template import Context
from django.core.exceptions import ValidationError
from django.conf import settings

from models import EmailMessageTemplate
from fields import validate_template_syntax
from utils import send_mail, send_mass_mail, mail_admins, mail_managers

class TemplateRetrievalTest(TestCase):
    """
    Ensure that template objects are retrieved correctly from the database based 
    on queries by name and object, respecting the enabled flag and the fallback 
    behavior for object-based queries.  Queries that do not match active 
    templates should raise exceptions.
    """
    fixtures = ['test_templates',]

    # Simple named template retrievals
    def test_retrieve_named_template(self):
        """Ensure the correct named template is returned"""
        template = EmailMessageTemplate.objects.get_template("Template 1")
        self.assertEqual(template.pk, 1)

    def test_retrieve_missing_named_template(self):
        """Ensure an exception is raised if the correct template is missing"""
        self.assertRaisesMessage(EmailMessageTemplate.DoesNotExist,
            "EmailMessageTemplate matching query does not exist.",
            lambda: EmailMessageTemplate.objects.get_template("Nonexistent Template"))

    def test_retrieve_disabled_named_template(self):
        """Ensure an exception is raised if the correct template is disabled"""
        self.assertRaisesMessage(EmailMessageTemplate.DoesNotExist,
            "EmailMessageTemplate matching query does not exist.",
            lambda: EmailMessageTemplate.objects.get_template("Template 3"))

    # Retrievals of templates with specified objects
    def test_retrieve_object_template(self):
        """"Ensure the correct template is returned when queried with name and object"""
        site = Site.objects.get(pk=1)
        template = EmailMessageTemplate.objects.get_template("Template 1", related_object=site)
        self.assertEqual(template.pk, 4)

    def test_retrieve_missing_object_template(self):
        """Ensure an exception is raised if a template specifed with bad name and object is missing"""
        site = Site.objects.get(pk=1)
        self.assertRaisesMessage(EmailMessageTemplate.DoesNotExist,
            "EmailMessageTemplate matching query does not exist.",
            lambda: EmailMessageTemplate.objects.get_template("Nonexistent Template", site))

    def test_retrieve_object_fallback_template(self):
        """
        Ensure the fallback (no object) template is returned if a template with
        the specifed object is missing
        """
        site = Site.objects.get(pk=2)
        template = EmailMessageTemplate.objects.get_template("Template 1", related_object=site)
        self.assertEqual(template.pk, 1)

    def test_retrieve_disabled_object_fallback_template(self):
        """
        Ensure the fallback (no object) template is returned if a template with
        the specifed object is disabled
        """
        site = Site.objects.get(pk=2)
        template = EmailMessageTemplate.objects.get_template("Template 2", related_object=site)
        self.assertEqual(template.pk, 2)


class TemplatePreparationTest(TestCase):
    """
    Ensure that template data is correctly produced when a template is 
    instantiated and prepared for sending.  This includes assembling the From, CC 
    and BCC address lists and rendering the subject and body templates. 
    """
    fixtures = ['test_templates',]
    
    def setUp(self):
        self.context = {'hello': '*HELLO*', 'world': '*WORLD*'}

    # Ensure the sender address is set correctly
    def test_default_from(self):
        """
        If not specified in the template or on the instance, the from address is 
        pulled from settings.  If specified, this will be the 
        EMAILMESSAGETEMPLATES_DEFAULT_FROM_EMAIL setting, else the DEFAULT_FROM_EMAIL 
        setting.
        """
        template = EmailMessageTemplate.objects.get_template("Template 1")
        with self.settings(DEFAULT_FROM_EMAIL='test1@example.com'):
            self.assertEqual(template.from_email, 'test1@example.com')
            with self.settings(EMAILMESSAGETEMPLATES_DEFAULT_FROM_EMAIL='test2@example.com'):
                self.assertEqual(template.from_email, 'test2@example.com')


    def test_template_specified_from(self):
        """
        If a from address is specified on the template, use that instead.
        """
        template = EmailMessageTemplate.objects.get_template("Template 2")
        with self.settings(DEFAULT_FROM_EMAIL='dontdoit@example.com'):
            self.assertEqual(template.from_email, 'example@example.com')

    def test_prepare_specified_from(self):
        """
        If a from address is specified on the template, use that instead.
        """
        template = EmailMessageTemplate.objects.get_template("Template 2")
        with self.settings(DEFAULT_FROM_EMAIL='dontdoit@example.com'):
            template.from_email='inprepare@example.com'
            self.assertEqual(template.from_email, 'inprepare@example.com')
    # Ensure the "to" address is set correctly

    def test_instance_to(self):
        """Ensure the "to" email set on the instance is used"""
        template = EmailMessageTemplate.objects.get_template("Template 2")
        template.to = ['inprepare@example.com']
        self.assertEqual(template.to, ['inprepare@example.com'])
    # Ensure the "CC" address list is set correctly

    def test_instance_cc(self):
        """Ensure the "cc" email list set o the instance is used"""
        template = EmailMessageTemplate.objects.get_template("Template 1")
        template.cc = ['inprepare@example.com', 'inprepare2@example.com']
        cc = template.cc
        cc.sort()
        self.assertEqual(cc, ['inprepare2@example.com', 'inprepare@example.com'])

    def test_template_cc(self):
        """
        Ensure the "cc" email list set in the template is used
        """
        template = EmailMessageTemplate.objects.get_template("Template 2")
        cc = template.cc
        cc.sort()
        self.assertEqual(cc, ['a@example.com', 'b@example.com'])

    def test_instance_template_cc(self):
        """
        Ensure the "cc" email list seton the instance is used in 
        conjunction with cc addresses in the template
        """
        template = EmailMessageTemplate.objects.get_template("Template 2")
        template.cc = ['inprepare@example.com', 'inprepare2@example.com']
        cc = template.cc
        cc.sort()
        self.assertEqual(cc, ['a@example.com', 'b@example.com',
                              'inprepare2@example.com', 'inprepare@example.com'])

    # Ensure the "BCC" address list is set correctly
    def test_instance_bcc(self):
        """Ensure the "bcc" email list set on the instance is used"""
        template = EmailMessageTemplate.objects.get_template("Template 1")
        template.bcc = ['inprepare@example.com', 'inprepare2@example.com']
        bcc = template.bcc
        bcc.sort()
        self.assertEqual(bcc, ['inprepare2@example.com', 'inprepare@example.com'])

    def test_template_bcc(self):
        """
        Ensure the "bcc" email list set in the template is used
        """
        template = EmailMessageTemplate.objects.get_template("Template 2")
        bcc = template.bcc
        bcc.sort()
        self.assertEqual(bcc, ['c@example.com', 'd@example.com'])

    def test_instance_template_bcc(self):
        """
        Ensure the "bcc" email list set on the instance is used in 
        conjunction with bcc addresses in the template
        """
        template = EmailMessageTemplate.objects.get_template("Template 2")
        template.bcc = ['inprepare@example.com', 'inprepare2@example.com']
        bcc = template.bcc
        bcc.sort()
        self.assertEqual(bcc, ['c@example.com', 'd@example.com',
                               'inprepare2@example.com', 'inprepare@example.com'])
    # Ensure the subject renders correctly

    def test_render_subject_template(self):
        """
        Ensure the subject renders as expected 
        """
        template = EmailMessageTemplate.objects.get_template("Template 1")
        template.context = self.context
        self.assertEqual(template.subject, "Test 1 Subject *HELLO*")

    def test_render_prefixed_subject_template(self):
        """
        Ensure the subject renders as expected with a specified prefix
        """
        template = EmailMessageTemplate.objects.get_template("Template 1")
        template.context = self.context
        template.subject_prefix = "[PREFIX] "
        self.assertEqual(template.subject, "[PREFIX] Test 1 Subject *HELLO*")
    # Ensure the body renders correctly

    def test_render_body_template(self):
        """
        Ensure the body renders as expected 
        """
        template = EmailMessageTemplate.objects.get_template("Template 1")
        template.context = self.context
        self.assertEqual(template.body, "Test 1 body *WORLD*")
    #Ensure the prepare method populates the message correctly

    def test_prepare_template(self):
        """
        Ensure the email parameters are set correctly by the prepare method 
        """
        template = EmailMessageTemplate.objects.get_template("Template 1")
        template.context=self.context
        template.from_email='from@example.com'
        template.to=['to@example.com']
        template.cc=['cc@example.com']
        template.bcc=['bcc@example.com']
        template.subject_prefix='[PREFIX] '

        self.assertEqual(template.subject, "[PREFIX] Test 1 Subject *HELLO*")
        self.assertEqual(template.body, "Test 1 body *WORLD*")
        self.assertEqual(template.from_email, 'from@example.com')
        self.assertEqual(template.to, ['to@example.com'])
        self.assertEqual(template.cc, ['cc@example.com'])
        self.assertEqual(template.bcc, ['bcc@example.com'])


class TemplateSendingTest(TestCase):
    """
    Ensure that the emails are actually composed and sent successfully
    """
    fixtures = ['test_templates',]
    
    def setUp(self):
        self.context = {'hello': '*HELLO*', 'world': '*WORLD*'}

    # Email sending
    def test_send_email_success(self):
        """Ensure that an email can be successfully sent to the outbox"""
        template = EmailMessageTemplate.objects.get_template("Template 1")
        template.context=self.context
        template.from_email='from@example.com'
        template.to=['to@example.com']
        template.cc=['cc@example.com']
        template.bcc=['bcc@example.com']
        template.subject_prefix='[PREFIX] '
        template.send()

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, '[PREFIX] Test 1 Subject *HELLO*')
        self.assertEqual(mail.outbox[0].body, "Test 1 body *WORLD*")
        self.assertEqual(mail.outbox[0].from_email, 'from@example.com')
        self.assertEqual(mail.outbox[0].to, ['to@example.com'])
        self.assertEqual(mail.outbox[0].cc, ['cc@example.com'])
        self.assertEqual(mail.outbox[0].bcc, ['bcc@example.com'])     

class HTMLTemplateTest(TestCase):
    """
    Ensure that HTML template data is correctly produced when a template is 
    instantiated and sent.  This includes rendering alternatives and 
    autogenerating content a required. 
    """
    fixtures = ['test_templates',]
    
    def setUp(self):
        self.context = {'hello': '*HELLO*', 'world': '*WORLD*'}
    
    def test_html_attachment(self):
        """Ensure that html content is included in HTML messages"""
        with self.settings(EMAILMESSAGETEMPLATES_ALLOW_HTML_MESSAGES=True):
            template = EmailMessageTemplate.objects.get_template("Template 5")
            template.context=self.context
            template.from_email='from@example.com'
            template.to=['to@example.com']
            template.send()
            
            # Test that one message has been sent.
            self.assertEqual(len(mail.outbox), 1)
            
            message = mail.outbox[0].message()
            
            #Test that the basic message setup is correct
            self.assertTrue(message.is_multipart())
            self.assertEqual(message.get_content_type(), 'multipart/alternative')
            self.assertEqual(message.get_default_type(), 'text/plain')
            
            #Test that there are two parts, with content types for text and html
            self.assertEqual(message.get_payload(0).get_content_type(), 'text/plain')
            self.assertEqual(message.get_payload(1).get_content_type(), 'text/html')
        
        
    def test_text_autogenreate(self):
        """
        Ensure that plain text content is correctly autogenerated from HTML 
        content
        """
        with self.settings(EMAILMESSAGETEMPLATES_ALLOW_HTML_MESSAGES=True): 
            template = EmailMessageTemplate.objects.get_template("Template 5")
            template.context=self.context
            template.from_email='from@example.com'
            template.to=['to@example.com']
            template.send()
            
            self.assertEqual(len(mail.outbox), 1)
            
            message = mail.outbox[0].message()
            
            self.assertTrue("""# *HELLO* *WORLD* in HTML!""" in message.get_payload(0).as_string())
            self.assertTrue("""<h1>*HELLO* *WORLD* in HTML!</h1>""" in message.get_payload(1).as_string())
    
    def test_html_disallowed(self):
        """
        Ensure that plain text content is is used when HTML emails are not 
        permitted by settings
        """
        with self.settings(EMAILMESSAGETEMPLATES_ALLOW_HTML_MESSAGES=False): 
            template = EmailMessageTemplate.objects.get_template("Template 6")
            template.context=self.context
            template.from_email='from@example.com'
            template.to=['to@example.com']
            template.send()
            
            self.assertEqual(len(mail.outbox), 1)
            
            message = mail.outbox[0].message()
            
            self.assertFalse(message.is_multipart())
            self.assertTrue("""*HELLO* *WORLD* in text!""" in message.as_string())
        
    def test_html_not_present(self):
        """
        Ensure that plain text messages don't automatically get HTML content
        """
        with self.settings(EMAILMESSAGETEMPLATES_ALLOW_HTML_MESSAGES=True):
            template = EmailMessageTemplate.objects.get_template("Template 1")
            template.context=self.context
            template.from_email='from@example.com'
            template.to=['to@example.com']
            template.send()
    
            # Test that one message has been sent.
            self.assertEqual(len(mail.outbox), 1)
            
            self.assertFalse(mail.outbox[0].message().is_multipart())


class TemplateValidatorTest(TestCase):
    """
    Ensure the template syntax validator correctly identifies invalid template 
    strings
    """

    def test_valid_template(self):
        """Ensure template validator passes valid templates"""
        validate_template_syntax("hello {% if world %} world {% else %} you {% "
                                 "endif %}")

    def test_invalid_template(self):
        """Ensure template validator rejects invalid templates"""
        self.assertRaises(ValidationError, 
            validate_template_syntax, 
            "hello {% if world %} world")


class UtilityFunctionTest(TestCase):
    """
    Test the behavior of the 4 utility functions: send_mail, send_mass_mail, 
    mail_admins, mail_managers
    """
    
    fixtures = ['test_templates',]
    
    def setUp(self):
        self.context = {'hello': '*HELLO*', 'world': '*WORLD*'}
        self.context2 = {'hello': '-GOODBYE-', 'world': '-EARTH-'}
 
    def test_send_mail(self):
        """Ensure the send_mail function works"""
        send_mail("Template 1", context=self.context, 
                  recipient_list=['to@example.com'])

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Test 1 Subject *HELLO*')
        self.assertEqual(mail.outbox[0].body, "Test 1 body *WORLD*")
        self.assertEqual(mail.outbox[0].to, ['to@example.com'])

    def test_send_mass_mail(self):
        """Ensure the send_mass_mail function works"""

        datatuple = [(self.context,'from1@example.com',['to1@example.com']),
                     (self.context2,'from2@example.com',['to2@example.com']),]
        send_mass_mail("Template 1", datatuple=datatuple)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 2)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Test 1 Subject *HELLO*')
        self.assertEqual(mail.outbox[0].body, "Test 1 body *WORLD*")
        self.assertEqual(mail.outbox[0].to, ['to1@example.com'])

        self.assertEqual(mail.outbox[1].subject, 'Test 1 Subject -GOODBYE-')
        self.assertEqual(mail.outbox[1].body, "Test 1 body -EARTH-")
        self.assertEqual(mail.outbox[1].to, ['to2@example.com'])

    def test_mail_admins(self):
        """Ensure the mail_admins function works"""
        with self.settings(ADMINS=(('a','admin1@example.com'),
                                   ('b','admin2@example.com'))):
            mail_admins("Template 1", context=self.context)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Test 1 Subject *HELLO*')
        self.assertEqual(mail.outbox[0].body, "Test 1 body *WORLD*")
        self.assertEqual(mail.outbox[0].to, ['admin1@example.com', 
                                             'admin2@example.com'])

    def test_mail_managers(self):
        """Ensure the mail_managers function works"""
        with self.settings(MANAGERS=(('a','admin1@example.com'),
                                     ('b','admin2@example.com'))):
            mail_managers("Template 1", context=self.context)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Test 1 Subject *HELLO*')
        self.assertEqual(mail.outbox[0].body, "Test 1 body *WORLD*")
        self.assertEqual(mail.outbox[0].to, ['admin1@example.com', 
                                             'admin2@example.com'])
