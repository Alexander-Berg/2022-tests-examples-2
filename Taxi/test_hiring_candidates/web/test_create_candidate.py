# pylint: disable=redefined-outer-name

import pytest

from hiring_candidates.internal import utils
from test_hiring_candidates import conftest

ROUTE = '/v1/salesforce/create-candidate'


@pytest.mark.parametrize('request_name', ['default'])
@conftest.main_configuration
async def test_create_candidate_idempotency(
        request_create_candidate,
        load_json,
        get_all_leads,
        get_all_candidates,
        request_name,
):
    make_request = request_create_candidate
    request = load_json('requests.json')[request_name]

    request_body = request['body']
    response = await make_request(body=request_body, code=request['code'])
    candidate_id = (await response.json())['candidate_id']

    response = await make_request(body=request_body, code=request['code'])
    candidate_id2 = (await response.json())['candidate_id']

    assert candidate_id2 == candidate_id

    candidates = get_all_candidates()
    assert len(candidates) == 1
    assert candidates[0]['id'] == candidate_id

    leads = get_all_leads()
    assert len(leads) == 1
    assert leads[0]['candidate_id'] == candidate_id
    assert leads[0]['lead_id'] == request_body['lead_id']

    # New Lead, same candidate
    request_body['lead_id'] = 'new_lead_id'
    response = await make_request(body=request_body, code=request['code'])
    candidate_id3 = (await response.json())['candidate_id']
    assert candidate_id3 == candidate_id

    leads = get_all_leads()
    assert len(leads) == 2
    assert leads[1]['candidate_id'] == candidate_id


@pytest.mark.parametrize(
    'request_name',
    [
        'default',
        'full',
        'full_empty_strings',
        'sf_null_strings',
        'no_phone',
        'personal_phone_id',
        'with_extra',
    ],
)
@conftest.main_configuration
async def test_create_candidate_different_args(
        request_create_candidate, get_all_leads, load_json, request_name,
):
    make_request = request_create_candidate
    request = load_json('requests.json')[request_name]
    body = request['body']
    await make_request(body=body, code=request['code'])

    leads = get_all_leads()

    if request['code'] == 200:
        assert leads
    else:
        assert not leads
        return

    ignore_fields = {
        'personal_phone_id',
        'user_login_creator',
        'license',
        'phone',
    }
    for field in ignore_fields:
        body.pop(field, None)

    lead_row = leads[0]
    converted_lead = utils.convert_db_to_api_keys(lead_row)
    for attr in body:
        if body[attr] in ('', None):
            continue
        assert converted_lead[attr] is not None, attr


@pytest.mark.parametrize('request_name', ['personal400'])
@conftest.main_configuration
async def test_create_candidate_personal400(
        mockserver, request_create_candidate, load_json, request_name,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/phones/store')
    def store_phones(_):
        doc = {'code': '400', 'message': 'Invalid phone number'}
        return mockserver.make_response(json=doc, status=400)

    request = load_json('requests.json')[request_name]
    await request_create_candidate(body=request['body'], code=request['code'])


@pytest.mark.parametrize('request_name', ['default'])
@conftest.main_configuration
async def test_create_candidate_same_lead_id_different_phone(
        request_create_candidate, get_all_leads, load_json, request_name,
):
    make_request = request_create_candidate
    request = load_json('requests.json')[request_name]
    body = request['body']
    await make_request(body=body, code=request['code'])

    # Make sure that phone is different
    body['phone'] = '+' + str(int(body['phone']) + 1)
    await make_request(body=body, code=400)

    assert len(get_all_leads()) == 1


@pytest.mark.parametrize('request_name', ['status_active_external_id'])
async def test_create_candidate_status_active_external_id(
        request_create_candidate, load_json, get_all_leads, request_name,
):
    request = load_json('requests.json')[request_name]
    body = request['body']
    await request_create_candidate(body=body, code=request['code'])

    leads = get_all_leads()
    expected_leads = load_json('expected_leads.json')[request_name]

    assert leads == expected_leads


@pytest.mark.parametrize('request_name', ['with_extra'])
@conftest.main_configuration
async def test_create_candidate_with_extra(
        request_create_candidate, load_json, get_all_leads, request_name,
):
    request = load_json('requests.json')[request_name]
    body = request['body']
    await request_create_candidate(body=body, code=request['code'])

    leads = get_all_leads()
    expected_leads = load_json('expected_leads.json')[request_name]

    assert leads == expected_leads
