import json as jsn
import logging
import os

import requests

logger = logging.getLogger(__file__)


def request(method, url, **kwargs):
    response = requests.request(method, url, **kwargs)
    if 'json' in kwargs:
        logger.debug('Request data: %s', kwargs['json'])
    if os.getenv('PRETTY_JSON_LOG'):
        try:
            response_text = '\n' + jsn.dumps(response.json(), indent=4)
        except ValueError:
            response_text = response.content
    else:
        response_text = response.content
    logger.debug('Link: %s, response: %s',
                 response.headers.get('X-YaRequestId'),
                 response_text)
    return response


def get(url, params=None, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('get', url, params=params, **kwargs)


def post(url, data=None, json=None, **kwargs):
    return request('post', url, data=data, json=json, **kwargs)


def put(url, data=None, json=None, **kwargs):
    return request('put', url, data=data, json=json, **kwargs)


def delete(url, data=None, json=None, **kwargs):
    return request('delete', url, data=data, json=json, **kwargs)
