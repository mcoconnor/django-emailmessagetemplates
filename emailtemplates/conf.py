from django.conf import settings
from appconf import AppConf

class MyAppConf(AppConf):
    
    DEFAULT_FROM_EMAIL = None
    """
    The address messages appear to come from.  Can be overridden for a 
    particular template or when a message is prepared.
    """
