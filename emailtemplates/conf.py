from django.conf import settings
from appconf import AppConf

class MyAppConf(AppConf):
    
    DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
    """
    The address messages appear to come from.  Can be overridden for a 
    particular template or when a message is prepared.
    """
        
    LOG_EMAILS = True
    """
    When enabled, attempts to send emails will be recorded in the Log model.  
    To prevent instances of a particular template to be logged when this is 
    enabled (due to low value or frequent sending, for example), set the 
    suppress_log field on the template model instance.
    """
        
    LOG_CONTENT = False
    """
    When enabled, the subject and body of the rendered email will be 
    retained in the log.  If you enable this be sure that you are purging 
    the logs regularly periodically to prevent excess data retention.
    """
        
    LOG_RETENTION_DAYS = 30
    """
    The number of days to save email logs.  This value is used by default in 
    the log purge management command. 
    """
        
    PURGE_FAILED_MESSAGES = True
    """
    If True, failed messagelogs will be purged on the same timeframe as 
    successes.  If you want to ensure failures stick around longer (if, for 
    example, you want to try to resend them), set this to False to prevent 
    automatic purges. 
    """
