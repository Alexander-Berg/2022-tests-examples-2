import json
import logging
import urllib2
import sys
import time
import datetime


CONNECTION_TIMEOUT = 20
DEFAULT_TIME_LIMIT = datetime.timedelta(days=65)


class RequestParams(object):
    def __init__(self, host):
        self.parameters = dict()
        self.host = host

    def append_parameter(self, url, name, value):
        if value is None:
            return url
        else:
            return url + ('?' if url == self.host else '&') + str(name) + '=' + str(value)

    def build_request(self):
        url = self.host
        for key in self.parameters:
            url = self.append_parameter(url, key, str(self.parameters[key]))

        return url


def run_request(request_params):
    logging.info('Connection to %s with timeout %.1f s.' % (request_params.build_request(), CONNECTION_TIMEOUT))
    for i in range(0, 10):
        try:
            response = urllib2.urlopen(request_params.build_request(), timeout=CONNECTION_TIMEOUT)
            return json.loads(response.read())
        except Exception as e:
            logging.error(e)
            time.sleep(i)
    raise Exception('Cannot run request %s' % request_params.build_request())


def get_commits_info():
    params = RequestParams('http://testenv.yandex-team.ru/autocheck/statistics_info')
    return run_request(params)


def get_available_commits():
    start_revision = None
    end_revision = None
    for _, v in get_commits_info().iteritems():
        if v.get('start_revision') is not None and v.get('end_revision') is not None:
            start_revision = min(start_revision, int(v['start_revision'])) if start_revision else v['start_revision']
            end_revision = max(end_revision, int(v['end_revision'])) if end_revision else v['end_revision']
    return start_revision, end_revision


def get_commits(start_revision, end_revision):
    params = RequestParams('http://testenv.yandex-team.ru/autocheck/statistics')
    params.parameters['start_revision'] = start_revision
    params.parameters['end_revision'] = end_revision
    return run_request(params)


def fetch(time_limit=None):
    time_limit = time_limit or DEFAULT_TIME_LIMIT
    right_now = datetime.datetime.now()

    def chunks(l, n):
        for i in xrange(0, len(l), n):
            yield l[i], l[min(i + n - 1, len(l) - 1)]

    def is_final_part(part):
        timestamps = [el['timestamp'] for el in part.values()]
        if len(timestamps) == 0:
            return False
        min_time = datetime.datetime.fromtimestamp(min(timestamps))
        return right_now - min_time > time_limit

    result = {}

    begin, end = get_available_commits()
    logging.info('full range is from {} to {}'.format(begin, end))
    for xfrom, xto in list(chunks(xrange(begin, end + 1), 1000))[::-1]:
        logging.info('fetching from {} to {}'.format(xfrom, xto))
        part = get_commits(xfrom, xto)
        result.update(part)
        if is_final_part(part):
            break

    return result


if __name__ == '__main__':
    json.dump(fetch(), sys.stdout, indent=4)
