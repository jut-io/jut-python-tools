
from datetime import datetime


def iso8601_to_epoch(iso8601):
    date = datetime.strptime(iso8601, "%Y-%m-%dT%H:%M:%S.%fZ")
    return int((date - datetime.utcfromtimestamp(0)).total_seconds())


def datetime_to_iso8601(date):
    """
    take a datetime object and return it formatted per ISO8601 date format spec

    """
    return '%s.%03dZ' % \
           (date.strftime('%Y-%m-%dT%H:%M:%S'), date.microsecond / 1000.0)

def now_iso8601():
    return datetime_to_iso8601(datetime.now())

def epoch_to_iso8601(epoch):
    return datetime_to_iso8601(datetime.utcfromtimestamp(epoch))



