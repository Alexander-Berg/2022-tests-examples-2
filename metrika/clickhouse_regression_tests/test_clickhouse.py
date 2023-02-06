import re

from requests import RequestException

import json
import logging

import allure

import pytest
from metrika.admin.python.clickhouse_regression_tests.queries import QUERIES
from metrika.pylib.clickhouse.lib import Query
from allure.constants import AttachmentType


@pytest.mark.parametrize('query', QUERIES, ids=lambda query: query.ticket)
def test_queries(clickhouse, query):
    logging.debug('Запрос %s %s', query, query.query_params)
    if query.ticket:
        allure.attach('Тикет', f'https://st.yandex-team.ru/{query.ticket}')
    allure.attach('Запрос', query.query)
    if query.query_params:
        allure.attach('Параметры', json.dumps(query.query_params), AttachmentType.JSON)

    try:
        answer = clickhouse.execute(Query(query.query, **query.query_params), timeout=300).data
        allure.attach('Код ответа', '200')
        logging.debug('Ответ %s', answer)
        if answer and isinstance(answer[0], bytes):
            answer = str(answer)
            allure.attach('Ответ', answer)
        else:
            allure.attach('Ответ', json.dumps(answer, indent=2), AttachmentType.JSON)
    except Exception as e:
        if isinstance(e, RequestException) and e.response is not None:
            answer = e.response.text
            allure.attach('Код ответа', str(e.response.status_code))
        else:
            answer = str(e)
        logging.debug('Ответ %s', answer)
        allure.attach('Ответ', answer)
        if query.success:
            raise Exception(answer)
    else:
        if isinstance(answer, str):
            m = re.search(r'Code: \d+.*?official build\)\)', answer)
            if m:
                raise Exception(m.group())

    if query.expected is not None:
        expected = query.expected
        if query.success:
            if not isinstance(query.expected, list):
                expected = [query.expected]
            assert answer == expected
        else:
            assert expected in answer
