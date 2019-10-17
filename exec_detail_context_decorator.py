import logging

from contextlib import ContextDecorator
from django.db import connection, reset_queries
from django.utils import timezone

logger = logging.getLogger(__name__)


class ExecutionLogger(ContextDecorator):
    def __init__(self, verbose, header, to_log):
        self.verbose = verbose
        self.header = header
        self.display_method = self._get_display_method(to_log)

    def __enter__(self):
        reset_queries()
        self.start_time = timezone.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = timezone.now()
        exec_time = self.end_time - self.start_time

        info_to_display = \
            f'{self.header}' \
            f'Total: {str(exec_time)} secs, {len(connection.queries)} DB queries\n'
        self.display_method(info_to_display)

        if self.verbose:
            for idx, query in enumerate(connection.queries, start=1):
                sql = query['sql']
                time = query['time']
                self.display_method(f'[{idx}] {time} secs\n{sql}\n')

    @staticmethod
    def _get_display_method(to_log):
        return logger.info if to_log else print


def exec_details(using=None, *,
                 verbose=False, header='', to_log=False):
    """
    Usage:
        Bare decorator: @exec_logger
        Decorator: @exec_logger(verbose=True, header='...', ...)
        Context manager: with exec_logger():
    :param using: (not used) the function being decorated
    :param verbose: show db query details
    :param header: info. to display ahead exec info.
    :param to_log: to log instead of to print directly
    """
    if callable(using):
        return ExecutionLogger(verbose, header, to_log)(using)
    else:
        return ExecutionLogger(verbose, header, to_log)

