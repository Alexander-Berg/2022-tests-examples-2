import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_h2h_authproxy_plugins import *  # noqa: F403 F401

try:
    import library.python.resource  # noqa: F401

    _IS_ARCADIA = True
except ImportError:
    _IS_ARCADIA = False

if _IS_ARCADIA:
    import logging
    import dataclasses

    @pytest.fixture(autouse=True)
    async def service_logs(taxi_bank_h2h_authproxy):
        levels = {
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'CRITICAL': logging.CRITICAL,
        }

        # Each log record is captured as a dictionary,
        # so we need to turn it back into a string
        def serialize_tskv(row):
            # these two will only lead to data duplication
            skip = {'timestamp', 'level'}

            # reorder keys so that 'text' is always in front
            keys = list(row.keys())
            keys.remove('text')
            keys.insert(0, 'text')

            return '\t'.join([f'{k}={row[k]}' for k in keys if k not in skip])

        async with taxi_bank_h2h_authproxy.capture_logs() as capture:
            # This hack tricks the client into thinking that
            # caches still need to be invalidated on the first call
            # so as not to break tests that depend on this behaviour
            # pylint: disable=protected-access
            taxi_bank_h2h_authproxy._client._state_manager._state = (
                dataclasses.replace(
                    # pylint: disable=protected-access
                    taxi_bank_h2h_authproxy._client._state_manager._state,
                    caches_invalidated=False,
                )
            )

            @capture.subscribe()
            # pylint: disable=unused-variable
            def log(**row):
                logging.log(
                    levels.get(row['level'], logging.DEBUG),
                    serialize_tskv(row),
                )

            yield capture


@pytest.fixture
def mock_remote(mockserver):
    def _func(
            url_path, request_body=None, response_code=200, response_body=None,
    ):
        if response_body is None:
            response_body = {}

        if not url_path.startswith('/'):
            url_path = f'/{url_path}'

        @mockserver.json_handler(url_path)
        def handler(request):
            if request.method != 'GET':
                assert request.json == request_body
            assert request.headers['X-Ya-Service-Ticket'] == 'MOCK_TICKET'
            return mockserver.make_response(
                status=response_code, json=response_body,
            )

        return handler

    return _func
