from django.core import mail
from django.test import TestCase
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

from models import EmailMessageTemplate, Log, EmailTemplateError

class TemplateRetrievalTest(TestCase):
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

    # Retreievals o templates with specified objects
    def test_retrieve_object_template(self):
        """"Ensure the correct template is returned when queried with name and object"""
	site = Site.objects.get(pk=1)
        template = EmailMessageTemplate.objects.get_template("Template 1",related_object=site)
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
        template = EmailMessageTemplate.objects.get_template("Template 1",related_object=site)
        self.assertEqual(template.pk, 1)

    def test_retrieve_disabled_object_fallback_template(self):
        """
        Ensure the fallback (no object) template is returned if a template with
        the specifed object is disabled
        """
	site = Site.objects.get(pk=2)
        template = EmailMessageTemplate.objects.get_template("Template 2",related_object=site)
        self.assertEqual(template.pk, 2)

class TemplateRenderTest(TestCase):
    fixtures = ['test_templates',]

    def test_render_subject_template(self):
        pass

    def test_render_invalid_subject_template(self):
        pass

    def test_render_body_template(self):
        pass

    def test_render_body_subject_template(self):
        pass

class TemplateSendingTest(TestCase):
    fixtures = ['test_templates',]

    # Email sending

    # Message logging
