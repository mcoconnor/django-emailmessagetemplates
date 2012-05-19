"""
Tools for sending templated emails
"""

import copy

from django.core.mail import get_connection

from models import EmailMessageTemplate, Log, EmailTemplateError
from utils import send_mail, send_mass_mail, mail_admins, mail_managers


__all__ = [EmailMessageTemplate, Log, EmailTemplateError, send_mail, 
           send_mass_mail, mail_admins, mail_managers]
