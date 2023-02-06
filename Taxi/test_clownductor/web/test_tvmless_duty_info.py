import pytest


@pytest.mark.parametrize(
    'request_params, status, duty_called, expected',
    [
        pytest.param(
            {'service_id': 1}, 200, True, 'response_service_id_1.json',
        ),
        pytest.param(
            {'service_id': 2}, 200, False, 'response_service_id_2.json',
        ),
        pytest.param(
            {'service_id': 2, 'get_full_list': True},
            200,
            False,
            'response_service_id_4.json',
            id='with_cache',
        ),
        pytest.param(
            {'service_id': 3}, 200, False, 'response_service_id_3.json',
        ),
        pytest.param({'service_id': 55}, 404, False, 'NOT_FOUND'),
        pytest.param(
            {'service_id': 1},
            200,
            False,
            'response_service_id_1_from_abc.json',
            marks=[pytest.mark.features_on('enable_use_abc_service_for_duty')],
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_db.sql'])
async def test_duty_info(
        taxi_clownductor_web,
        request_params,
        status,
        expected,
        load_json,
        mockserver,
        duty_called,
):
    @mockserver.json_handler('/client-abc/v4/duty/on_duty/')
    def client_abc_handler(request):
        if request.query.get('schedule__slug') == 'primary_shedule_service':
            return [
                {
                    'person': {'login': 'main_duty'},
                    'start_datetime': '2022-06-09T12:00:00+03:00',
                    'end_datetime': '2022-06-10T12:00:00+03:00',
                },
            ]
        if request.query.get('service__slug') == 'common_abc_slug':
            return [
                {
                    'person': {'login': 'assistant1'},
                    'start_datetime': '2022-06-08T12:00:00+03:00',
                    'end_datetime': '2022-06-10T12:00:00+03:00',
                },
                {
                    'person': {'login': 'assistant2'},
                    'start_datetime': '2022-06-09T12:00:00+03:00',
                    'end_datetime': '2022-06-10T12:00:00+03:00',
                },
                {
                    'person': {'login': 'main_duty'},
                    'start_datetime': '2022-06-09T12:00:00+03:00',
                    'end_datetime': '2022-06-10T12:00:00+03:00',
                },
            ]
        return []

    @mockserver.json_handler('/duty-api/api/duty_group')
    def duty_group_handler(request):
        assert request.query['group_id'] == 'elrusso_band'
        return {
            'result': {
                'data': {
                    'currentEvent': {'user': 'karachevda'},
                    'suggestedEvents': [{'user': 'test_user'}],
                    'staffGroups': ['test_group'],
                    'people': ['karachevda', 'elrusso', 'web-sheriff'],
                },
                'ok': True,
            },
        }

    response = await taxi_clownductor_web.post(
        '/v1/services/duty_info/', json=request_params,
    )
    assert response.status == status
    data = await response.json()
    if status == 404:
        assert expected == data['code']
    else:
        assert load_json(expected) == data

    if duty_called:
        assert duty_group_handler.times_called == 1
    else:
        assert not duty_group_handler.times_called

    if request_params.get('service_id') == 1 and not duty_called:
        assert client_abc_handler.times_called == 2
