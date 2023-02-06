import jinja2
import logging
import re
import time

from sandbox.projects.common import decorators
from sandbox.projects.common import requests_wrapper
from sandbox.projects.common import file_utils as fu
from sandbox.projects.websearch.TestXmlSearch2 import const as txs_const


@decorators.retries(max_tries=3, delay=3, backoff=2)
def requests_get_r(*args, **kwargs):
    """
    Same as `requests_wrapper.get_r` but with custom retry policy
    and additional checking of empty responses
    (less backoff and delay)
    """
    raise_for_empty_response = kwargs.pop('raise_for_empty_response', False)
    r = requests_wrapper.get(*args, **kwargs)

    if r.status_code == 500 or r.status_code == 429:
        # handle hamster overload. Sample log: https://paste.yandex-team.ru/700720
        logging.info('Got %s http error code, hamster is overloaded, sleeping for 120s...', r.status_code)
        time.sleep(120)

    r.raise_for_status()

    if raise_for_empty_response and not r.text:
        raise Exception("Empty response received. ")

    return r


def url_is_valid(url):
    logging.debug('Validating URL %s', url)
    url_match = re.search(r'(?P<schema>^https?:/+)(?P<fqdn>.+?)(/|\?|$)', url)

    if not url_match:
        logging.debug('URL is not valid')
        return False

    matched_url = url_match.groupdict()
    schema, fqdn = matched_url['schema'], matched_url['fqdn']
    logging.debug('Schema: %s, FQDN: %s', schema, fqdn)

    if len(fqdn) < 4:  # "m.ua" is the smallest domain we've seen in real production
        logging.debug('FQDN length < 4, FQDN %s seems to be invalid', fqdn)
        return False

    if '.' not in fqdn:
        logging.debug("There is no '.' in FQDN %s, this FQDN is not valid", fqdn)
        return False

    # http://stackoverflow.com/questions/2180465/can-domain-name-subdomains-have-an-underscore-in-it

    logging.debug("Validation successfully done")
    return True


def check_invalid_urls(docs):
    for url in docs:
        if not url_is_valid(url):
            logging.debug("Detected invalid url in XML response: '%s'", url)
            return 'invalid url'
    return None


def write_html_file(diff, file_path):
    if not diff:
        fu.write_file(file_path, '<!DOCTYPE html><html><body>No diff</body></html>')
        return

    jinja_template = jinja2.Template(txs_const.XML_SEARCH_TEMPLATE)
    html = jinja_template.render(diff=diff)
    fu.write_file(file_path, html.encode('utf-8'))
