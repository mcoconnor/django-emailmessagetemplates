def send_mail(name, related_object=None, context={}, from_email=None, 
              recipient_list=[], fail_silently=False, auth_user=None, 
               auth_password=None, connection=None):
    """
    Easy wrapper for sending a single templated message to a recipient list.  
    The template to use is retrieved from the database based on the name and 
    related_object (optional) fields.

    All members of the recipient list will see the other recipients in the 'To' 
    field.

    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.
    """

    try:
        template = EmailMessageTemplate.objects.get(name=name,related_object=related_object)
    except EmailMessageTemplate.DoesNotExist:
        if not related_object:
            raise
        template = EmailMessageTemplate.objects.get(name=name,related_object=None)

    connection = connection or get_connection(username=auth_user,
                                              password=auth_password,
                                              fail_silently=fail_silently)

    template.prepare(context=context, from_email=from_email, to=recipient_list, 
                     connection=connection)
    return template.send()


def send_mass_mail(name, related_object=None, datatuple=(), fail_silently=False, 
                   auth_user=None, auth_password=None, connection=None):
    """
    Given a datatuple of (context, from_email, recipient_list), renders and 
    sends a message to each recipient list. Returns the number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    If a related object is specified, we'll first try to retrieve a template 
    that matches both the name and the object, and if none exists, we'll try to 
    retrieve a template with the specified name without a related object instead
    (to support situations where some objects have a specialized template, but, 
    when none exists, we want to fall back to a default). 
    """

    try:
        template = EmailMessageTemplate.objects.get(name=name,related_object=related_object)
    except EmailMessageTemplate.DoesNotExist:
        if not related_object:
            raise
        template = EmailMessageTemplate.objects.get(name=name,related_object=None)

    connection = connection or get_connection(username=auth_user,
                                              password=auth_password,
                                              fail_silently=fail_silently)

    messages = [copy.deepcopy(template).prepare(context=context, 
                                                from_email=from_email, 
                                                to=recipient_list, 
                                                connection=connection)
                for (context, from_email, recipient_list) in datatuple]
 
    return connection.send_messages(messages)


def mail_admins(name, related_object=None, context={}, fail_silently=False, 
                connection=None):
    """Sends a message to the admins, as defined by the ADMINS setting."""
    return send_mail(name,related_object,context,fail_silently=fail_silently,
                     recipient_list=[a[1] for a in settings.ADMINS],
                     connection=connection)


def mail_managers(name, related_object=None, context={}, fail_silently=False, 
                connection=None):
    """Sends a message to the managers, as defined by the MANAGERS setting."""
    return send_mail(name,related_object,context,fail_silently=fail_silently,
                     recipient_list=[a[1] for a in settings.MANAGERS],
                     connection=connection)
