# -*- coding: utf-8 -*-
import json
import urlparse

import bson
import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.external import startrack
from taxi.external import zendesk
from taxiadmin.views import common


@pytest.mark.parametrize(
    'ticket_id,order_id,expected_result,expected_ticket_type',
    [
        (
            '123',
            'order_id1',
            False,
            ''
        ),
        (
            '341',
            'order_id1',
            False,
            ''
        ),
        (
            '342',
            'order_id2',
            False,
            ''
        ),
        (
            '121',
            'order_id4',
            False,
            ''
        ),
        (
            '5b86c169779fb3358c81a11a',
            'order_id6',
            True,
            'chatterbox'
        ),
        (
            '5b86c169779fb3358c81a111',
            'order_id7',
            False,
            ''
        ),
        (
            '5b86c169779fb3358c81a11aa',
            'order_id6',
            False,
            ''
        ),
        (
            '5b86c228779fb3358c81a11b',
            'order_id6',
            True,
            'chatterbox'
        ),
        (
            '5b86c228779fb3358c81a11b',
            'order_id7',
            True,
            'chatterbox'
        ),
        (
            'TESTQUEUE-123',
            'order_id7',
            True,
            'startrack'
        ),
        (
            'TESTQUEUE-456',
            'order_id7',
            False,
            ''
        ),
    ]
)
@pytest.mark.filldb(
    order_proc='test_check_ticket_new',
    finance_tickets_zendesk='test_check_ticket_new',
    tariff_settings='check_new'
)
@pytest.inline_callbacks
def test_check_ticket_soft_mode(
    areq_request, patch, ticket_id, order_id,
    expected_result, expected_ticket_type
):

    @patch('taxi.external.archive.get_order_proc_by_id')
    @async.inline_callbacks
    def get_order_proc_by_id(order_id, log_extra=None):
        yield async.return_value({})

    @patch('taxi.external.zendesk.get_zendesk_client_by_id')
    def get_zendesk_client_by_id(zendesk_id):
        return zendesk.ZendeskApiClient(
            '', '', '', zendesk_id
        )

    @patch('taxi.external.zendesk.check_ticket_existence')
    @async.inline_callbacks
    def check_ticket_existence(client, ticket_id):
        yield async.return_value(ticket_id[-1] == '1')

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'GET'
        assert url.startswith('http://chatterbox.taxi.yandex.net')
        parsed_url = urlparse.urlparse(url)
        chat_id = parsed_url.path.split('/')[3]
        if bson.ObjectId.is_valid(chat_id):
            return areq_request.response(200, json.dumps({}))
        return areq_request.response(404)

    @patch('taxi.external.startrack.get_ticket_info')
    def dummy_get_ticket(ticket, profile=None):
        if ticket == 'TESTQUEUE-123':
            return {}
        raise startrack.NotFoundError

    result, ticket_type = yield common.check_zendesk_ticket(ticket_id, order_id)
    assert result == expected_result
    if result:
        assert ticket_type == expected_ticket_type


@pytest.mark.parametrize(
    'ticket_id,order_id,ticket_type,expected_result',
    [
        (
            '5b86c169779fb3358c81a111',
            'order_id1',
            'chatterbox',
            False
        ),
        (
            '5b87e04c779fb3358c81a161',
            'order_id1',
            'chatterbox',
            True
        ),
        (
            '5b86c169779fb3358c81a111',
            'order_id1',
            'zendesk',
            False
        ),
        (
            '5b87e04c779fb3358c81a151',
            'order_id2',
            'chatterbox',
            True
        ),
        (
            '5b87e04c779fb3358c81a11d',
            'order_id2',
            'chatterbox',
            False
        ),
        (
            '5b87e04c779fb3358c81a141',
            'order_id2',
            'chatterbox',
            True
        ),
        (
            '5b87e04c779fb3358c81a131',
            'order_id3',
            'chatterbox',
            True
        ),
        (
            '5b87e04c779fb3358c81a121',
            'order_id4',
            'chatterbox',
            True,
        ),
        (
            '5b87e04c779fb3358c81a111',
            'order_id5',
            'chatterbox',
            True
        ),
        (
            'some_existing_samsara_ticket',
            'order_id5',
            'samsara',
            True
        ),
        (
            'some_unknown_samsara_ticket',
            'order_id5',
            'samsara',
            False,
        ),
        (
            'some_existing_salesforce_ticket',
            'order_id5',
            'yandextaxib2b_salesforce',
            True,
        ),
        (
            'some_unknown_salesforce_ticket',
            'order_id5',
            'yandextaxib2b_salesforce',
            False,
        ),
    ]
)
@pytest.mark.filldb(
    order_proc='test_check_ticket_new',
    finance_tickets_zendesk='test_check_ticket_new',
    tariff_settings='check_new'
)
@pytest.inline_callbacks
@pytest.mark.config(
    STRICT_CHECK_FINANCE_TICKET=True
)
def test_check_ticket_strict_mode(
        monkeypatch, areq_request, patch, ticket_id, order_id,
        ticket_type, expected_result
):
    monkeypatch.setattr(
        settings, 'SALESFORCE_API_PROFILES',
        {
            'yandextaxib2b': {
                'client_id': 'some_client_id',
                'client_secret': 'some_client_secret',
                'grant_type': 'password',
                'password': 'some_password',
                'username': 'some_username',
                'url': 'https://yandextaxib2b--copy.my.salesforce.com',
            }
        }
    )

    @patch('taxi.external.archive.get_order_proc_by_id')
    @async.inline_callbacks
    def get_order_proc_by_id(order_id, log_extra=None):
        yield async.return_value({})

    @patch('taxi.external.zendesk.get_zendesk_client_by_id')
    def get_zendesk_client_by_id(zendesk_id):
        return zendesk.ZendeskApiClient(
            '', '', '', zendesk_id
        )

    @patch('taxi.external.zendesk.check_ticket_existence')
    @async.inline_callbacks
    def check_ticket_existence(client, ticket_id):
        yield async.return_value(ticket_id[-1] == '1')

    @areq_request
    def requests_request(method, url, **kwargs):
        if ticket_type == 'chatterbox':
            assert method == 'GET'
            assert url.startswith('http://chatterbox.taxi.yandex.net')
            parsed_url = urlparse.urlparse(url)
            id_ = parsed_url.path.split('/')[3]
            if id_[-1] == '1':
                return areq_request.response(200, json.dumps({}))
        elif ticket_type == 'samsara':
            assert method == 'GET'
            assert url.startswith('https://test-api.samsara.yandex-team.ru')
            if 'existing_samsara_ticket' in url:
                return areq_request.response(403, json.dumps({}))
        else:
            assert url.startswith('https://yandextaxib2b--copy.my.salesforce.com')
            if 'oauth2/token' in url:
                assert method == 'POST'
                return areq_request.response(
                    200, json.dumps({'access_token': 'some_token'})
                )
            assert method == 'GET'
            if 'existing_salesforce_ticket' in url:
                return areq_request.response(200, json.dumps({}))

        return areq_request.response(404)

    result, given_ticket_type = yield common.check_zendesk_ticket(
        ticket_id, order_id, ticket_type
    )
    assert given_ticket_type == ticket_type
    assert result == expected_result
