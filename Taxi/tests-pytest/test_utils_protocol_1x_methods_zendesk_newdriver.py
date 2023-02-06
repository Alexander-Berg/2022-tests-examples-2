import datetime
import json
import mocks
import pytest
import uuid

from taxi.core import async, db
from utils.protocol_1x.methods import zendesk_newdriver

MAGIC_UUID = u'2830227ea6944f95b894d27df5f9ace4'
NOW = datetime.datetime(2019, 7, 3)


@async.inline_callbacks
def _get_response(request):
    method = zendesk_newdriver.Method()
    response = yield method.POST(request)
    async.return_value(response)


@pytest.mark.parametrize(
    'content,expected_response,expected_response_code,db_req',
    [
        (
                {'name': 'driver'},
                {'error': "Incorrect phone field given"},
                406,
                None,
        ),
        (
                {
                    'phone': '+79000000000',
                    'name': 'drvier',
                    'description': 'body',
                    'subject': 'theme',
                    'utm_campaign': 100,
                },
                {},
                None,
                {
                    '_id': MAGIC_UUID,
                    'updated': NOW,
                    'phone_pd_id': 'phone_pd_id',
                    'name': 'drvier',
                    'description': 'body',
                    'subject': 'theme',
                    'utm_campaign': 100,
                },
        ),
        (
                {
                    'phone': '+79000000000',
                    'name': 'drvier',
                    'description': 'body',
                    'subject': 'theme',
                    'utm_source': 'content',
                    'bad_field': 'bad_not_going_to_base',
                },
                {},
                None,
                {
                    '_id': MAGIC_UUID,
                    'updated': NOW,
                    'phone_pd_id': 'phone_pd_id',
                    'name': 'drvier',
                    'description': 'body',
                    'subject': 'theme',
                    'utm_source': 'content',
                },
        ),
    ])
@pytest.inline_callbacks
@pytest.mark.now(NOW.isoformat())
def test_zendesk_newdriver(content, expected_response,
                           expected_response_code, db_req, patch):
    @patch('uuid.uuid4')
    def uuid4():
        return uuid.UUID(MAGIC_UUID)

    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def store(data_type, request_value, validate, log_extra=None):
        assert not validate
        assert data_type == 'phones'
        assert request_value == content['phone']
        yield async.return_value({'id': 'phone_pd_id'})

    request = mocks.FakeRequest(content=json.dumps(content))
    response = yield _get_response(request)
    assert response == expected_response
    assert request.response_code == expected_response_code
    res = db.newdriver_requests.find_one({'_id': MAGIC_UUID}).result
    if db_req:
        assert res == db_req
