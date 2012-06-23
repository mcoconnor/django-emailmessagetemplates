from django.conf import settings


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class AppSettings(object):

    @ClassProperty
    @classmethod
    def EMAILTEMPLATES_DEFAULT_FROM_EMAIL(cls):
        """
        The address messages appear to come from.  Can be overridden for a 
        particular template or when a message is prepared.
        """
        return getattr(settings, 
                       'EMAILTEMPLATES_DEFAULT_FROM_EMAIL', 
                       settings.DEFAULT_FROM_EMAIL)

    @ClassProperty
    @classmethod
    def EMAILTEMPLATES_LOG_EMAILS(cls):
        """
        When enabled, attempts to send emails will be recorded in the Log model.  
        To prevent instances of a particular template to be logged when this is 
        enabled (due to low value or frequent sending, for example), set the 
        suppress_log field on the template model instance.
        """
        return getattr(settings, 'EMAILTEMPLATES_LOG_EMAILS', True)

    @ClassProperty
    @classmethod
    def EMAILTEMPLATES_LOG_CONTENT(cls):
        """
        When enabled, the subject and body of the rendered email will be 
        retained in the log.  If you enable this be sure that you are purging 
        the logs regularly periodically to prevent excess data retention.
        """
        return getattr(settings, 'EMAILTEMPLATES_LOG_CONTENT', False)

    @ClassProperty
    @classmethod
    def EMAILTEMPLATES_LOG_RETENTION_DAYS(cls):
        """
        The number of days to save email logs.  This value is used by default in 
        the log purge management command. 
        """
        return getattr(settings, 'EMAILTEMPLATES_LOG_RETENTION_DAYS', 30)

    @ClassProperty
    @classmethod
    def EMAILTEMPLATES_PURGE_FAILED_MESSAGES(cls):
        """
        If True, failed messagelogs will be purged on the same timeframe as 
        successes.  If you want to ensure failures stick around longer (if, for 
        example, you want to try to resend them), set this to False to prevent 
        automatic purges. 
        """
        return getattr(settings, 'EMAILTEMPLATES_PURGE_FAILED_MESSAGES', True)
