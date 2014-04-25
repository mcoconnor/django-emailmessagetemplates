 Django Email Templates
=======================
&copy; 2014 Michael O'Connor, http://www.mcoconnor.net
https://github.com/mcoconnor/django-emailtemplates

In many cases, users will want to be able to edit the emails sent by your application without having to go to developers to change hard-coded email content.  This package provides a Django app that allows users to edit email content and review email logs with an easy-to-integrate developer API.

Installation
------------
Django Email Templates is a standard Django app.  To add it to a project, just include `'emailtemplates'` in the `INSTALLED_APPS` section of your `settings.py` file. 

Usage
-----
The central piece of functionality in this app is the EmailMessageTemplate class, which is a Django model that also inherits from Django's `EmailMessage` class.  Usage is derived from its parents: to select a template to send, query for it as a model.  To send an email, first populate the message with the template context, recipients, and other data, and then call the `send` method.  For example:
    
    t = EmailMessageTemplate.objects.get(name='Hello World')
    t.context = {'a':'hello','b':'world'}
    t.to = ['michael@mcoconnor.net',]
    t.attach_file('/docs/Hello.pdf')
    t.send()
    
Email templates support the same attributes that `EmailMessage`s do, including `to`, `cc`, `bcc`, `from_email`, `headers`, and `attachments`.

Convenience Functions
---------------------
The email convenience functions provided by Django replicated for message templates.  These include `send_mail`, `send_mass_mail`, `mail_admins`, `mail_managers` and are used similarly:


    send_mail(name, related_object=None, context={}, from_email=None,
              recipient_list=[], fail_silently=False, auth_user=None,
              auth_password=None, connection=None)

    send_mass_mail(name, related_object=None, datatuple=(), fail_silently=False,
                   auth_user=None, auth_password=None, connection=None)  

    mail_admins(name, related_object=None, context={}, fail_silently=False,
                connection=None)
                    
    mail_managers(name, related_object=None, context={}, fail_silently=False,
                  connection=None)

Differences from `EmailMessage`
-----------------------------
While `EmailMessageTemplate` behaves like Django's `EmailMessage` in many ways, there are some differences:

* Subject and body values cannot be set directly; instead they're constructed from templates saved in the model rendered against the specified context
* If `from_email` is not specified when a message is prepared, the value defaults first to the `sender` set on the template model, then to the `EMAILTEMPLATES_DEFAULT_FROM_EMAIL` setting
* Values required by the message (e.g the recipients) cannot be set in the `EmailMessageTemplate` constructor like they are for `EmailMessage` (since normally you will retrieve an existing model instance rather than constructing one).  Instead, they must be set individually on the instance.


Settings
--------
**`EMAILTEMPLATES_DEFAULT_FROM_EMAIL`**

Default: The `DEFAULT_FROM_EMAIL` value from your project's settings.

The default email address to use for message sent from templates.  This is can be overridden on a per-template basis by setting the `sender` field on the template model instance.  It can be overridden on a per-email basis by setting the `from_email` attribute on an instantiated `EmailMessageTemaple` object or using the `from_email` argument to any of the convenience functions.
