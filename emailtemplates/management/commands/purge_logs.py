from optparse import make_option
from datetime import timedelta, datetime

from django.core.management.base import BaseCommand

from emailtemplates.conf import settings
from emailtemplates.models import Log

class Command(BaseCommand):
    help = "Purges old email logs from the database"

    option_list = BaseCommand.option_list + (
        make_option('--retentiondays',
            action='store',
            type='int',
            dest='retention_days',
            default=None,
            help='Number of days of logs to retain.  Defaults to the EMAILTEMPLATES_LOG_RETENTION_DAYS setting'),
        make_option('--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force all logs beyond the retention threshold to be purged, regardless of the EMAILTEMPLATES_PURGE_FAILED_MESSAGES setting'),
        )

    def handle(self, *test_labels, **options):
        """
        Clear out the logs prior to the specified time period
        """
        verbosity = int(options['verbosity'])
        retain_days = options['retention_days'] if options['retention_days'] is not None else settings.EMAILTEMPLATES_LOG_RETENTION_DAYS
        retention_threshold = datetime.now() - timedelta(retain_days)

        if verbosity > 0:
            print "Deleting log entries prior to", retention_threshold
        logs = Log.objects.filter(date__lt=retention_threshold)

        if not (settings.EMAILTEMPLATES_PURGE_FAILED_MESSAGES or options['force']):
            if verbosity > 1:
                print "Retaining failed message logs."
            logs = logs.exclude(status=Log.STATUS.FAILURE)

        if verbosity > 1:
            print "Found {0} entries to delete.".format(logs.count())
        logs.delete()
        
