import pytest


PERSONAL_PHONE_ID = 'personal_phone_id'
EXP3_SEGMENTATION_CONSUMER = 'eats-support-misc/segmentation'
EXP3_SEGMENTATION_OVERRIDES_NAME = (
    'eats_support_misc_eater_segmentation_override_rules'
)

RT_XARON_EATER_SEGMENTATION_URL = '/rt-xaron/lavka/support-abuse-scoring/user'


@pytest.mark.parametrize(
    """rt_xaron_response_mock,expected_response""",
    [
        pytest.param(
            {'result': [{'name': 'eats_green', 'value': True}]},
            {'segmentation': 'good'},
            id='good without override',
        ),
        pytest.param(
            {'result': [{'name': 'eats_grey', 'value': True}]},
            {'segmentation': 'other'},
            id='other without override',
        ),
        pytest.param(
            {'result': [{'name': 'eats_red', 'value': True}]},
            {'segmentation': 'bad'},
            id='bad without override',
        ),
        pytest.param(
            {'result': [{'name': 'eats_grey', 'value': True}]},
            {'segmentation': 'good'},
            id='other overrides with good',
            marks=pytest.mark.client_experiments3(
                consumer=EXP3_SEGMENTATION_CONSUMER,
                config_name=EXP3_SEGMENTATION_OVERRIDES_NAME,
                args=[
                    {
                        'name': 'personal_phone_id',
                        'type': 'string',
                        'value': PERSONAL_PHONE_ID,
                    },
                ],
                value={'override': 'good'},
            ),
        ),
        pytest.param(
            {'result': [{'name': 'eats_green', 'value': True}]},
            {'segmentation': 'other'},
            id='good downgrades to other',
            marks=pytest.mark.client_experiments3(
                consumer=EXP3_SEGMENTATION_CONSUMER,
                config_name=EXP3_SEGMENTATION_OVERRIDES_NAME,
                args=[
                    {
                        'name': 'personal_phone_id',
                        'type': 'string',
                        'value': PERSONAL_PHONE_ID,
                    },
                ],
                value={'downgrade': 'other'},
            ),
        ),
        pytest.param(
            {'result': [{'name': 'eats_green', 'value': True}]},
            {'segmentation': 'good'},
            id='unexpected override value',
            marks=pytest.mark.client_experiments3(
                consumer=EXP3_SEGMENTATION_CONSUMER,
                config_name=EXP3_SEGMENTATION_OVERRIDES_NAME,
                args=[
                    {
                        'name': 'personal_phone_id',
                        'type': 'string',
                        'value': PERSONAL_PHONE_ID,
                    },
                ],
                value={'override': 'unexpected'},
            ),
        ),
        pytest.param(
            {'result': [{'name': 'eats_green', 'value': True}]},
            {'segmentation': 'good'},
            id='unexpected downgrade value',
            marks=pytest.mark.client_experiments3(
                consumer=EXP3_SEGMENTATION_CONSUMER,
                config_name=EXP3_SEGMENTATION_OVERRIDES_NAME,
                args=[
                    {
                        'name': 'personal_phone_id',
                        'type': 'string',
                        'value': PERSONAL_PHONE_ID,
                    },
                ],
                value={'downgrade': 'unexpected'},
            ),
        ),
        pytest.param(
            {'result': [{'name': 'eats_green', 'value': True}]},
            {'segmentation': 'other'},
            id='override has more priority than downgrade',
            marks=pytest.mark.client_experiments3(
                consumer=EXP3_SEGMENTATION_CONSUMER,
                config_name=EXP3_SEGMENTATION_OVERRIDES_NAME,
                args=[
                    {
                        'name': 'personal_phone_id',
                        'type': 'string',
                        'value': PERSONAL_PHONE_ID,
                    },
                ],
                value={'override': 'other', 'downgrade': 'bad'},
            ),
        ),
    ],
)
async def test_green_flow(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        rt_xaron_response_mock,
        expected_response,
):
    @mockserver.json_handler(RT_XARON_EATER_SEGMENTATION_URL)
    def _mock_rt_xaron_eater_segmentation(request):
        assert request.json == {'user_personal_phone_id': PERSONAL_PHONE_ID}
        return mockserver.make_response(
            status=200, json=rt_xaron_response_mock,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-eater-segmentation',
        params={'personal_phone_id': PERSONAL_PHONE_ID},
    )

    assert response.status == 200
    assert await response.json() == expected_response


@pytest.mark.parametrize(
    """rt_xaron_response_mock""",
    [
        pytest.param({'result': []}, id='empty rt_xaron response'),
        pytest.param(
            {'result': [{'name': 'eats_red', 'value': False}]},
            id='rt_xaron respond with false',
        ),
        pytest.param(
            {'result': [{'name': 'unexpected', 'value': True}]},
            id='rt_xaron respond with unexpected name',
        ),
    ],
)
async def test_not_found(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        rt_xaron_response_mock,
):
    @mockserver.json_handler(RT_XARON_EATER_SEGMENTATION_URL)
    def _mock_rt_xaron_eater_segmentation(request):
        assert request.json == {'user_personal_phone_id': PERSONAL_PHONE_ID}
        return mockserver.make_response(
            status=200, json=rt_xaron_response_mock,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-eater-segmentation',
        params={'personal_phone_id': PERSONAL_PHONE_ID},
    )

    assert response.status == 404
