import datetime


def format_execution_timestamp(now, step=0):
    now += datetime.timedelta(milliseconds=step)
    string = now.strftime('%Y-%m-%dT%H:%M:%S.%f')
    return string[:-3] + 'Z'
