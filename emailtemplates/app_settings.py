from django.conf import settings

"""
The address messages appear to come from.  Can be overridden for a particular 
template or when a message is prepared.
"""
EMAILTEMPLATES_DEFAULT_FROM_EMAIL = getattr(settings, 'EMAILTEMPLATES_DEFAULT_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)

"""
When enabled, attempts to send emails will be recorded in the Log model.  To 
prevent instances of a particular template to be logged when this is enabled 
(due to low value or frequent sending, for example), set the suppress_log field 
on the template model instance.
"""
EMAILTEMPLATES_LOG_EMAILS = getattr(settings, 'EMAILTEMPLATES_LOG_EMAILS', True)

"""
When enabled, the body of the rendered email will be retained in the log.  If 
you enable this be sure that you are purging the logs regularly periodically to 
prevent excess data retention.
"""
EMAILTEMPLATES_LOG_BODY = getattr(settings, 'EMAILTEMPLATES_LOG_BODY', False)

"""
The number of days to save email logs.  This value is used by default in the log 
purge management command. 
"""
EMAILTEMPLATES_LOG_RETENTION_DAYS = getattr(settings, 'EMAILTEMPLATES_LOG_RETENTION_DAYS', 30)
