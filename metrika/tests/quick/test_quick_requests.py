from metrika.pylib.http import request
from metrika.pylib.log import base_logger, init_logger
import pytest
import time
from requests.exceptions import HTTPError, ReadTimeout
from requests import Session
import requests_mock

logger = base_logger.manager.getLogger('metrika.pylib.http.tests')
init_logger('mtutils', stdout=True)
init_logger('urllib3', stdout=True)


def test_quick_requests():
    with requests_mock.Mocker() as m:
        s = Session()
        retry_kwargs = dict(
            tries=3,
            delay=0.1,
            backoff=1,
        )

        m.get('http://a.a', status_code=503)
        start_time = time.time()
        with pytest.raises(HTTPError):
            request(
                url='http://a.a',
                retry_if_http_error=True,
                retry_kwargs=retry_kwargs,
                session=s,
            )

        spent_time = time.time() - start_time

        assert 0.2 <= spent_time <= 1.0

        m.get('http://b.b', exc=ReadTimeout)

        start_time = time.time()
        with pytest.raises(ReadTimeout):
            request(
                url='http://b.b',
                retry_kwargs=retry_kwargs,
                session=s,
            )

        spent_time = time.time() - start_time

        assert 0.2 <= spent_time <= 1.0
