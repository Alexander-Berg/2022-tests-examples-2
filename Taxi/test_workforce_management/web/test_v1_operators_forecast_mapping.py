import pytest

from workforce_management.common import utils
from workforce_management.storage.postgresql import forecast as forecasts_repo

VALUES_URI = 'v1/operators/forecast/mapping/values'
MODIFY_URI = 'v1/operators/forecast/mapping/modify'
X_DOMAIN = 'taxi'
X_YA_UID = 'uid1'
HEADERS = {'X-WFM-DOMAIN': X_DOMAIN, 'X-Yandex-UID': X_YA_UID}
REVISION_ID = '2022-05-05T00:00:00.0 +0000'


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_FORECAST_SETTINGS={
        'taxi': {
            'source_type': 'yt_v2',
            'source_path': '',
            'end_of_period_minutes': 20100,
        },
    },
)
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_skills.sql', 'forecast_mappings.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        pytest.param(
            {'skills': ['pokemon']},
            200,
            [
                {
                    'skill': 'pokemon',
                    'mappings': [
                        [
                            {'key': 'city', 'value': 'spb'},
                            {'key': 'line', 'value': 'disp_1'},
                        ],
                        [{'key': 'line', 'value': 'disp_2'}],
                    ],
                },
            ],
            id='base',
        ),
        pytest.param(
            {'skills': []},
            200,
            [
                {
                    'skill': 'hokage',
                    'mappings': [[{'key': 'line', 'value': 'disp_3'}]],
                },
                {
                    'skill': 'pokemon',
                    'mappings': [
                        [
                            {'key': 'city', 'value': 'spb'},
                            {'key': 'line', 'value': 'disp_1'},
                        ],
                        [{'key': 'line', 'value': 'disp_2'}],
                    ],
                },
            ],
            id='base_filter_none',
        ),
        pytest.param({}, 200, [], id='base_null_filter'),
        pytest.param({'skills': ['taxi']}, 200, [], id='base_no_matches'),
    ],
)
async def test_values(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_result,
):
    res = await taxi_workforce_management_web.post(
        VALUES_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    if expected_status > 200:
        return

    data = await res.json()
    data = utils.expected_fields(data['records'], expected_result)
    assert data == expected_result


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_FORECAST_SETTINGS={
        'taxi': {
            'source_type': 'yt_v2',
            'source_path': '',
            'end_of_period_minutes': 20100,
        },
    },
)
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_skills.sql', 'forecast_mappings.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [
                            [
                                {'key': 'line', 'value': 'disp_1'},
                                {'key': 'city', 'value': 'msk'},
                            ],
                        ],
                    },
                ],
                'modify_mode': 'insert',
            },
            200,
            {
                'pokemon': [
                    {'city': 'msk', 'line': 'disp_1'},
                    {'city': 'spb', 'line': 'disp_1'},
                    {'line': 'disp_2'},
                ],
            },
            id='base_insert',
        ),
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [
                            [
                                {'key': 'line', 'value': 'disp_4'},
                                {'key': 'city', 'value': 'spb'},
                            ],
                            [
                                {'key': 'line', 'value': 'disp_2'},
                                {'key': 'brand', 'value': 'yndx'},
                            ],
                        ],
                        'revision_id': REVISION_ID,
                    },
                    {
                        'skill': 'hokage',
                        'mappings': [[{'key': 'line', 'value': 'disp_1'}]],
                        'revision_id': REVISION_ID,
                    },
                ],
                'modify_mode': 'replace',
            },
            200,
            {
                'hokage': [{'line': 'disp_1'}],
                'pokemon': [
                    {'city': 'spb', 'line': 'disp_4'},
                    {'brand': 'yndx', 'line': 'disp_2'},
                ],
            },
            id='base_replace',
        ),
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [],
                        'revision_id': REVISION_ID,
                    },
                ],
                'modify_mode': 'replace',
            },
            200,
            {},
            id='base_delete',
        ),
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [
                            [
                                {'key': 'line', 'value': 'disp_1'},
                                {'key': 'brand', 'value': 'yndx'},
                                {'key': 'city', 'value': 'msk'},
                                {'key': 'city', 'value': 'spb'},
                            ],
                        ],
                        'revision_id': REVISION_ID,
                    },
                ],
                'modify_mode': 'replace',
            },
            200,
            {
                'pokemon': [
                    {'brand': 'yndx', 'city': 'msk', 'line': 'disp_1'},
                    {'brand': 'yndx', 'city': 'spb', 'line': 'disp_1'},
                ],
            },
            id='multi_choice_replace',
        ),
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [
                            [
                                {'key': 'line', 'value': 'disp_1'},
                                {'key': 'brand', 'value': 'yndx'},
                                {'key': 'city', 'value': 'msk'},
                            ],
                        ],
                    },
                    {
                        'skill': 'hokage',
                        'mappings': [
                            [
                                {'key': 'line', 'value': 'disp_1'},
                                {'key': 'city', 'value': 'msk'},
                            ],
                        ],
                    },
                ],
                'modify_mode': 'insert',
            },
            200,
            {
                'hokage': [
                    {'city': 'msk', 'line': 'disp_1'},
                    {'line': 'disp_3'},
                ],
                'pokemon': [
                    {'brand': 'yndx', 'city': 'msk', 'line': 'disp_1'},
                    {'city': 'spb', 'line': 'disp_1'},
                    {'line': 'disp_2'},
                ],
            },
            id='override_in_request',
        ),
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [
                            [
                                {'key': 'line', 'value': 'disp_3'},
                                {'key': 'brand', 'value': 'yndx'},
                                {'key': 'city', 'value': 'msk'},
                            ],
                        ],
                    },
                ],
                'modify_mode': 'insert',
            },
            200,
            {
                'pokemon': [
                    {'brand': 'yndx', 'city': 'msk', 'line': 'disp_3'},
                    {'city': 'spb', 'line': 'disp_1'},
                    {'line': 'disp_2'},
                ],
            },
            id='override_existing',
        ),
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [
                            [
                                {'key': 'line', 'value': 'disp_4'},
                                {'key': 'not_present', 'value': 'err'},
                            ],
                        ],
                    },
                ],
                'modify_mode': 'insert',
            },
            400,
            None,
            id='extra_keys',
        ),
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [
                            [
                                {'key': 'line', 'value': 'disp_1'},
                                {'key': 'city', 'value': 'spb'},
                            ],
                            [
                                {'key': 'line', 'value': 'disp_2'},
                                {'key': 'city', 'value': 'msk'},
                            ],
                        ],
                        'revision_id': 'ERR-05-05T00:00:00.0 +0000',
                    },
                ],
                'modify_mode': 'replace',
            },
            400,
            None,
            id='wrong_revision_format',
        ),
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [
                            [
                                {'key': 'line', 'value': 'disp_1'},
                                {'key': 'city', 'value': 'spb'},
                            ],
                            [
                                {'key': 'line', 'value': 'disp_2'},
                                {'key': 'city', 'value': 'msk'},
                            ],
                        ],
                        'revision_id': '2020-05-05T00:00:00.0 +0000',
                    },
                ],
                'modify_mode': 'replace',
            },
            409,
            None,
            id='wrong_revision_version',
        ),
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [
                            [
                                {'key': 'line', 'value': 'disp_1'},
                                {'key': 'brand', 'value': 'yndx'},
                            ],
                        ],
                    },
                    {
                        'skill': 'hokage',
                        'mappings': [
                            [
                                {'key': 'line', 'value': 'disp_1'},
                                {'key': 'city', 'value': 'msk'},
                            ],
                        ],
                    },
                ],
                'modify_mode': 'insert',
            },
            409,
            None,
            id='conflict_in_request',
        ),
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [[{'key': 'line', 'value': 'disp_3'}]],
                    },
                ],
                'modify_mode': 'insert',
            },
            409,
            None,
            id='conflict_existing_insert',
        ),
        pytest.param(
            {
                'records': [
                    {
                        'skill': 'pokemon',
                        'mappings': [[{'key': 'line', 'value': 'disp_3'}]],
                        'revision_id': REVISION_ID,
                    },
                ],
                'modify_mode': 'replace',
            },
            409,
            None,
            id='conflict_existing_replace',
        ),
    ],
)
async def test_modify(
        web_context,
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_result,
):
    res = await taxi_workforce_management_web.post(
        MODIFY_URI, json=tst_request, headers=HEADERS,
    )

    assert res.status == expected_status
    if expected_status > 200:
        return

    req_skills = [rec['skill'] for rec in tst_request['records']]
    forecasts_db = forecasts_repo.ForecastRepo(web_context)
    async with forecasts_db.master.acquire() as connection:
        records = await forecasts_db.get_forecasts_mappings(
            connection, skills=req_skills,
        )

    skill_mappings = {rec['skill']: rec['mappings'] for rec in records}
    assert skill_mappings == expected_result
