#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import logging
import time
import urllib
import urllib2


def get_url(url, instance='', cookie=None, user_agent=None, http_request_host=None, http_ip=None, data=None, headers=None):
    if isinstance(url, unicode): url = url.encode('UTF-8')
    if isinstance(instance, unicode): instance = instance.encode('UTF-8')

    url_full = instance + url
    logging.debug('Get url: ' + url_full)
    req = urllib2.Request(url_full, data=data)
    if cookie:
        req.add_header('Cookie', cookie)
    if user_agent:
        req.add_header('User-Agent', user_agent)
    if http_ip:
        req.add_header('X-Forwarded-For-Y', http_ip)
    if http_request_host is None: #if default:
        http_request_host = 'suggest.yandex.net'
    req.add_header('Host', http_request_host)

    if headers:
        for name, value in headers.items():
            req.add_header(name, value)

    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            response = urllib2.urlopen(req)
            answer = response.read()
            response.close()
            return answer
        except Exception, e:
            logging.error("Warning: can't open url (%s), retrying %s" % (e, url_full))
            time.sleep(1)
            if attempt == max_attempts - 1:
                raise

def assert_test_fail(test_name, url, expected, got):
    if isinstance(test_name, unicode): test_name = url.encode('UTF-8')
    if isinstance(url, unicode): url = url.encode('UTF-8')
    if isinstance(expected, unicode): expected = expected.encode('UTF-8')
    if isinstance(got, unicode): got = got.encode('UTF-8')

    if len(got) > 2000:
        if not isinstance(got, unicode): got = got.decode('UTF-8')
        got = (got[0:2000] + '... [skipped] ...').encode('UTF-8')

    fail_text = """-------------------------- FAIL --------------------------
test name: %s
url: %s
expected: %s
got     : %s""" % (test_name, url, expected, got)

    for line in fail_text.split('\n'):
        logging.error(line)

    return fail_text

def form_url(url='', instance='', handler='', params='', query=''):
    if isinstance(url, unicode): url = url.encode('UTF-8')
    if isinstance(instance, unicode): instance = instance.encode('UTF-8')
    if isinstance(query, unicode): query = query.encode('UTF-8')

    url_full = instance + handler + url
    if query:
        url_full = url_full + 'part=%s&' % urllib.quote_plus(query)
    if params:
        url_full = url_full + '&'.join(params) + '&'

    logging.debug('Formed url: ' + url_full)
    return url_full
