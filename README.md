 Django Email Templates
=======================
&copy; 2012 Michael O'Connor, http://www.mcoconnor.net
https://github.com/mcoconnor/django-emailtemplates

In many cases, users will want to be able to edit the emails sent by your application without having to go to developers to change hard-coded email content.  This package provides a Django app that allows users to edit email content and review email logs with an easy-to-integrate developer API.

Installation
------------

Usage
-----
The central piece of functionality in this app is the EmailMessageTemplate class, which is a Django model that also inherits from Django's EmailMessage class.  Usage is derived from its parents: to select a template to send, query for it as a model.  To send an email, first populate and render it by calling the `prepare` method (analogous to the EmailMessage constructor) with the template context, recipients, and other data, and then call the `send` method.  For example:
    
    t = EmailMessageTemplate.objects.get(name='Hello World')
    t.prepare(context={'a':'hello','b':'world'},to=['michael@mcoconnor.net',])
    t.attach_file('/docs/Hello.pdf')
    t.send()

Deployment
---------
If you have message logging enabled, your log table may grow to be very large, depending on the volume of emails sent by your application.  To ensure that this table doesn't grow out of control, be sure to set up a cronjob to call the `emailtemplates_purge_logs` management command periodically.  This will delete all logs more than `settings.EMAILTEMPLATES_LOG_RETENTION_DAYS` old.


Settings
--------
`EMAILTEMPLATES_DEFAULT_FROM_EMAIL`
`EMAILTEMPLATES_LOG_EMAILS`
`EMAILTEMPLATES_LOG_BODY`
`EMAILTEMPLATES_LOG_RETENTION_DAYS`
