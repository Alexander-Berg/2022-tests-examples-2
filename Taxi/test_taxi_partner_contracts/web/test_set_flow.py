import copy
import json

import aiohttp.test_utils
import pytest

HEADERS = {
    'X-YaTaxi-Api-Key': 'a8f5513cc4c84d18b56acd86bdd691ed',
    'Content-Type': 'application/json',
}

SAMPLE_CODE = 'sample_code'
SAMPLE_DUP = 'sample_1'

FLOW_CODE_NEW = 'new_flow_code'
FLOW_CODE_DUP = 'close_contract_refresh_oferta_corporate'
FLOW_DATA = {
    'code': FLOW_CODE_NEW,
    'is_automate_registration': True,
    'stages': [
        {
            'code': f'{SAMPLE_CODE}_stage',
            'sample_names': [SAMPLE_CODE],
            'fallback_sample': None,
        },
    ],
}
FLOW_DATA_2 = {
    'code': FLOW_CODE_NEW,
    'is_automate_registration': True,
    'stages': [
        {
            'code': f'{SAMPLE_CODE}_stage_2',
            'sample_names': [SAMPLE_CODE],
            'fallback_sample': None,
        },
    ],
}
FLOW_DATA_DUP = {
    'code': FLOW_CODE_NEW,
    'is_automate_registration': True,
    'stages': [
        {
            'code': f'{SAMPLE_DUP}_stage',
            'sample_names': [SAMPLE_DUP],
            'fallback_sample': None,
        },
    ],
}
FLOW_DATA_DUP_COUNTRY = {
    'code': FLOW_CODE_DUP,
    'is_automate_registration': True,
    'stages': [
        {
            'code': '__default__',
            'sample_names': [SAMPLE_DUP],
            'fallback_sample': None,
        },
    ],
}
FLOW_DATA_DUP_COUNTRY_WITH_VERSION = {
    'version': 2,
    'code': FLOW_CODE_DUP,
    'is_automate_registration': True,
    'stages': [
        {
            'code': '__default__',
            'sample_names': [SAMPLE_DUP],
            'fallback_sample': None,
        },
    ],
}
FLOW_DATA_DUP_COUNTRY_WITH_WRONG_VERSION = {
    'version': 3,
    'code': FLOW_CODE_DUP,
    'is_automate_registration': True,
    'stages': [
        {
            'code': '__default__',
            'sample_names': [SAMPLE_DUP],
            'fallback_sample': None,
        },
    ],
}

SAMPLE_DATA = {
    'code': SAMPLE_CODE,
    'sample_type': 'some_sample_type',
    'fields': [
        {'field': 'clid', 'field_type': 'from_form', 'name': 'clid'},
        {'field_type': 'default', 'name': 'change_name', 'value': 'contracts'},
    ],
}
SAMPLE_DATA_DUP = copy.deepcopy(SAMPLE_DATA)
SAMPLE_DATA_DUP['code'] = SAMPLE_DUP

RESPONSE_SAMPLE_NOT_FOUND = {
    'status': 'error',
    'errors': [
        {
            'field': None,
            'message': (
                f'sample_manager. error SampleNotFoundError:'
                f' Not found sample, sample_name={SAMPLE_CODE},'
                f' field_name=None'
            ),
            'sample': SAMPLE_CODE,
        },
    ],
}
RESPONSE_DUPLICATE_SAMPLE = {
    'status': 'error',
    'errors': [
        {
            'field': None,
            'message': (
                f'sample_manager. error DuplicateNamesError:'
                f' Duplicate samples, sample_name={SAMPLE_CODE},'
                f' field_name=None'
            ),
            'sample': SAMPLE_CODE,
        },
    ],
}
RESPONSE_VERSION_ERROR = {
    'status': 'error',
    'message': (
        'Flow close_contract_refresh_oferta_corporate for country '
        'rus has no version 3, sample_name=None, field_name=None'
    ),
    'code': 'VERSION_ERROR',
}
CHANGE_FLOW_MESSASE = (
    f'sample_manager. error ChangeFlowForSample: Change flow, stage'
    f' from (\'{FLOW_CODE_DUP}\', \'__default__\')'
    f' to (\'new_flow_code\', \'{SAMPLE_DUP}_stage\')'
    f', sample_name={SAMPLE_DUP}, field_name=None'
)
RESPONSE_CHANGE_FLOW = {
    'status': 'error',
    'errors': [
        {'field': None, 'message': CHANGE_FLOW_MESSASE, 'sample': SAMPLE_DUP},
    ],
}
RESPONSE_OK = {'status': 'ok'}

TEST_CASES = [
    (
        # normal set flow (without stage sent in sample)
        {'flow_data': FLOW_DATA, 'linked_samples': [SAMPLE_DATA]},
        200,
        RESPONSE_OK,
        3,
    ),
    (
        # FLOW_DATA_2['stages'][0]['sample_names'] has 'sample_code'
        # which is absent in 'linked_samples'
        {'flow_data': FLOW_DATA_2, 'linked_samples': [SAMPLE_DATA_DUP]},
        400,
        RESPONSE_SAMPLE_NOT_FOUND,
        2,
    ),
    (
        # FLOW_DATA_2['stages'][0]['sample_names'] has 'sample_code'
        # which is present in 'linked_samples'
        {
            'flow_data': FLOW_DATA_2,
            'linked_samples': [SAMPLE_DATA, SAMPLE_DATA_DUP],
        },
        200,
        RESPONSE_OK,
        3,
    ),
    (
        # 'linked_samples' has two samples with 'sample_code'
        {
            'flow_data': FLOW_DATA_2,
            'linked_samples': [SAMPLE_DATA, SAMPLE_DATA_DUP, SAMPLE_DATA],
        },
        400,
        RESPONSE_DUPLICATE_SAMPLE,
        2,
    ),
    (
        # FLOW_DATA_DUP['stages'][0]['sample_names'] has 'sample_1'
        # which is present in database with different (flow, stage)
        {'flow_data': FLOW_DATA_DUP, 'linked_samples': [SAMPLE_DATA_DUP]},
        400,
        RESPONSE_CHANGE_FLOW,
        2,
    ),
    (
        # FLOW_DATA_DUP_COUNTRY['stages'][0]['sample_names'] has 'sample_1'
        # which is present in database with same (flow, stage)
        # so it can be replaced (with config off) (if same country)
        {
            'flow_data': FLOW_DATA_DUP_COUNTRY,
            'linked_samples': [SAMPLE_DATA_DUP],
        },
        200,
        RESPONSE_OK,
        2,
    ),
    (
        # FLOW_DATA_DUP_COUNTRY['stages'][0]['sample_names'] has 'sample_1'
        # which is present in database with same (flow, stage)
        # so it can be replaced (with config off) (if same country)
        {
            'flow_data': FLOW_DATA_DUP_COUNTRY_WITH_VERSION,
            'linked_samples': [SAMPLE_DATA_DUP],
        },
        200,
        RESPONSE_OK,
        2,
    ),
    (
        # FLOW_DATA_DUP_COUNTRY['stages'][0]['sample_names'] has 'sample_1'
        # which is present in database with same (flow, stage)
        # so it can be replaced (with config off) (if same country)
        {
            'flow_data': FLOW_DATA_DUP_COUNTRY_WITH_WRONG_VERSION,
            'linked_samples': [SAMPLE_DATA_DUP],
        },
        409,
        RESPONSE_VERSION_ERROR,
        2,
    ),
    (
        # FLOW_DATA_DUP_COUNTRY['stages'][0]['sample_names'] has 'sample_1'
        # which is present in database with same (flow, stage)
        # so it can be saved (with config off) with another country
        {
            'flow_data': FLOW_DATA_DUP_COUNTRY,
            'linked_samples': [SAMPLE_DATA_DUP],
            'country_code': 'arm',
        },
        200,
        RESPONSE_OK,
        3,
    ),
    (
        # normal set flow (with stage in sample)
        {
            'flow_data': FLOW_DATA,
            'linked_samples': [
                dict(SAMPLE_DATA, stage=f'{SAMPLE_CODE}_stage'),
            ],
        },
        200,
        RESPONSE_OK,
        3,
    ),
]


@pytest.mark.config(ADMIN_FLOW_UNIQUENESS_BY_COUNTRY=False)
@pytest.mark.parametrize(
    'request_data,expected_status,expected_content,expected_db_count',
    TEST_CASES,
)
async def test_set_flow_old(
        web_app_client: aiohttp.test_utils.TestClient,
        request_data: dict,
        expected_status: int,
        expected_content: dict,
        expected_db_count: int,
        db: pytest.fixture,
) -> None:
    await _sub_test_set_flow(
        web_app_client,
        request_data,
        expected_status,
        expected_content,
        expected_db_count,
        db,
    )


CHANGE_FLOW_COUNTRY_MESSAGE = (
    f'sample_manager. error ChangeFlowForSample:'
    f' Change country, flow, stage'
    f' from (\'rus\', \'{FLOW_CODE_DUP}\', \'__default__\')'
    f' to (\'arm\', \'{FLOW_CODE_DUP}\', \'__default__\')'
    f', sample_name={SAMPLE_DUP}, field_name=None'
)
CHANGE_FLOW_COUNTRY_MESSAGE_2 = (
    f'sample_manager. error ChangeFlowForSample:'
    f' Change country, flow, stage'
    f' from (\'rus\', \'{FLOW_CODE_DUP}\', \'__default__\')'
    f' to (\'rus\', \'{FLOW_CODE_NEW}\', \'{SAMPLE_DUP}_stage\')'
    f', sample_name={SAMPLE_DUP}, field_name=None'
)
RESPONSE_CHANGE_FLOW_COUNTRY = {
    'status': 'error',
    'errors': [
        {
            'field': None,
            'message': CHANGE_FLOW_COUNTRY_MESSAGE,
            'sample': SAMPLE_DUP,
        },
    ],
}
RESPONSE_CHANGE_FLOW_2 = {
    'status': 'error',
    'errors': [
        {
            'field': None,
            'message': CHANGE_FLOW_COUNTRY_MESSAGE_2,
            'sample': SAMPLE_DUP,
        },
    ],
}

TEST_CASES_NEW = copy.deepcopy(TEST_CASES)
TEST_CASES_NEW[4] = (
    # FLOW_DATA_DUP['stages'][0]['sample_names'] has 'sample_1'
    # which is present in database with different (country, flow, stage)
    {'flow_data': FLOW_DATA_DUP, 'linked_samples': [SAMPLE_DATA_DUP]},
    400,
    RESPONSE_CHANGE_FLOW_2,
    2,
)
TEST_CASES_NEW[-2] = (
    # FLOW_DATA_DUP_COUNTRY['stages'][0]['sample_names'] has 'sample_1'
    # which is present in database with same (country, flow, stage)
    # so it cannot be saved (with config on) with different country
    {
        'flow_data': FLOW_DATA_DUP_COUNTRY,
        'linked_samples': [SAMPLE_DATA_DUP],
        'country_code': 'arm',
    },
    400,
    RESPONSE_CHANGE_FLOW_COUNTRY,
    2,
)


@pytest.mark.config(ADMIN_FLOW_UNIQUENESS_BY_COUNTRY=True)
@pytest.mark.parametrize(
    'request_data,expected_status,expected_content,expected_db_count',
    TEST_CASES_NEW,
)
async def test_set_flow_new(
        web_app_client: aiohttp.test_utils.TestClient,
        request_data: dict,
        expected_status: int,
        expected_content: dict,
        expected_db_count: int,
        db: pytest.fixture,
) -> None:
    await _sub_test_set_flow(
        web_app_client,
        request_data,
        expected_status,
        expected_content,
        expected_db_count,
        db,
    )


async def _sub_test_set_flow(
        web_app_client: aiohttp.test_utils.TestClient,
        request_data: dict,
        expected_status: int,
        expected_content: dict,
        expected_db_count: int,
        db: pytest.fixture,
) -> None:

    flow_code = request_data['flow_data']['code']
    country_code = request_data.pop('country_code', 'rus')
    response = await web_app_client.put(
        f'/admin/v1/flow/?flow_code={flow_code}&country_code={country_code}',
        data=json.dumps(request_data),
        headers=HEADERS,
    )
    content = await response.text()
    content = json.loads(content)

    assert (response.status, content) == (expected_status, expected_content), (
        'response status {}, expected {}, '
        'response content {!r}, expected {!r}'.format(
            response.status, expected_status, content, expected_content,
        )
    )

    stage_name = request_data['flow_data']['stages'][0]['code']
    query = {
        'flow_name': flow_code,
        'country_code': country_code,
        'stages.0.code': stage_name,
    }
    assert (await db.partner_flows.count()) == expected_db_count
    if response.status == 200:
        new_flow = await db.partner_flows.find_one(query)
        assert new_flow['is_automate_registration']
        assert new_flow['stages'] == request_data['flow_data']['stages']
        for stage in new_flow['stages']:
            for sample_name in stage['sample_names']:
                db_sample = await db.partner_samples.find_one(
                    {'name': sample_name},
                )
                assert (
                    db_sample is not None
                ), 'not found sample "{}" in database'.format(sample_name)
                assert db_sample['flow'] == flow_code
                assert (
                    db_sample.get('stage') == stage['code']
                ), 'bad stage in sample "{}"'.format(sample_name)
    elif response.status != 409:
        new_flow = await db.partner_flows.find_one(query)
        assert new_flow is None
