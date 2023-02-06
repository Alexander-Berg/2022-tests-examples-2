# pylint: disable=redefined-outer-name
import datetime
import uuid

import pytest

from hiring_candidates.internal import utils
from test_hiring_candidates import conftest


ROUTE = '/v1/salesforce/update-candidate'


@pytest.fixture  # noqa: F405
async def make_request(taxi_hiring_candidates_web):
    async def func(body, code):
        response = await taxi_hiring_candidates_web.post(ROUTE, json=body)
        assert response.status == code
        return response

    return func


@pytest.mark.parametrize(
    'create_requests_name, request_name',
    [
        ('default', 'default'),
        ('empty', 'empty_leads'),
        ('default', 'full'),
        ('default', 'full_empty_strings'),
        ('default', 'sf_null_strings'),
        ('default', 'empty'),
        ('default', 'with_extra'),
        ('with_extra', 'default'),
        ('with_extra', 'with_extra'),
    ],
)
@conftest.main_configuration
async def test_update_candidate(
        request_create_candidate,
        make_request,
        load_json,
        get_all_leads,
        create_requests_name,
        request_name,
):
    candidate_id = uuid.uuid4().hex
    for data in load_json('create_requests.json')[create_requests_name]:
        response = await request_create_candidate(data)
        candidate_id = (await response.json())['candidate_id']

    request = load_json('requests.json')[request_name]
    body = request['body']
    body['candidate_id'] = candidate_id

    await make_request(body=body, code=request['code'])
    if request['code'] != 200:
        return

    all_leads = get_all_leads()
    lead = next(
        lead for lead in all_leads if lead['lead_id'] == body['lead_id']
    )
    converted_lead = utils.convert_db_to_api_keys(lead)

    ignore_fields = {'license', 'user_login_creator'}
    ignore_values = {'', None}
    for field, value in body['payload'].items():
        if field in ignore_fields:
            continue
        if not isinstance(value, dict) and value in ignore_values:
            continue
        value_db = converted_lead[field]
        if isinstance(value_db, datetime.datetime):
            value_db = value_db.isoformat()
        assert value_db == value, field


@pytest.mark.parametrize(
    'create_requests_name, request_name', [('default', 'personal_error')],
)
@conftest.main_configuration
async def test_update_candidate_personal400(
        mockserver,
        request_create_candidate,
        make_request,
        load_json,
        request_name,
        create_requests_name,
):
    candidate_id = uuid.uuid4().hex
    for data in load_json('create_requests.json')[create_requests_name]:
        response = await request_create_candidate(data)
        candidate_id = (await response.json())['candidate_id']

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def store_licenses(_):
        doc = {'code': '400', 'message': 'Invalid phone number'}
        return mockserver.make_response(json=doc, status=400)

    request = load_json('requests.json')[request_name]
    body = request['body']
    body['candidate_id'] = candidate_id

    await make_request(body=body, code=request['code'])


@pytest.mark.parametrize('request_name', ['status_active_external_id'])
@conftest.main_configuration
async def test_update_candidate_status_active_external_id(
        request_create_candidate,
        make_request,
        load_json,
        get_all_leads,
        request_name,
):
    candidate_id = uuid.uuid4().hex
    for data in load_json('create_requests.json')['default']:
        response = await request_create_candidate(data)
        candidate_id = (await response.json())['candidate_id']

    request = load_json('requests.json')[request_name]
    body = request['body']
    body['candidate_id'] = candidate_id

    await make_request(body=body, code=request['code'])

    leads = get_all_leads()
    expected_leads = load_json('expected_leads.json')[request_name]

    assert leads == expected_leads
