import logging

import pytest

from taxi_buildagent import utils


@pytest.mark.parametrize('log_level', [logging.DEBUG, logging.INFO])
def test_init_logger(log_level):
    logger = logging.getLogger()
    initial_handlers = logger.handlers.copy()
    utils.init_logger(log_level)
    new_handlers = set(logger.handlers) - set(initial_handlers)
    assert len(new_handlers) == 2
    for handler in new_handlers:
        assert isinstance(handler, logging.StreamHandler)
    new_levels = {h.level for h in new_handlers}
    assert new_levels == {log_level, logging.WARNING}


@pytest.mark.parametrize(
    'headers,link,url',
    [
        (
            {'Link': '<next_url>; rel="next", <last_url>; rel="last"'},
            'next',
            'next_url',
        ),
        (
            {'Link': '<next_url>; rel="next", <last_url>; rel="last"'},
            'last',
            'last_url',
        ),
        (
            {'Link': '<next_url>; rel="next", <not_so_next>; rel="next"'},
            'next',
            'next_url',
        ),
    ],
)
def test_parse_link_header(stub, headers, link, url):
    assert url == utils.parse_link_header(stub(headers=headers), link)
