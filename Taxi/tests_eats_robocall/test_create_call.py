import pytest


@pytest.mark.pgsql('eats_robocall', files=['add_calls.sql', 'add_tokens.sql'])
@pytest.mark.experiments3(filename='scenarios.json')
@pytest.mark.parametrize(
    'request_body, token, expected_status_code, expected_task_id',
    [
        (
            {
                'personal_phone_id': 'default_phone_id',
                'scenario_name': 'scenario_1',
                'context': {'eater_id': '1337', 'country_code': 'ru'},
                'payload': {'abonents_name': ['aba', 'caba']},
            },
            'x_idempotency_token: 1',
            400,
            None,
        ),
        # (
        #     {
        #         'personal_phone_id': 'default_phone_id',
        #         'scenario_name': 'scenario_1',
        #         'context': {'eater_id': '1337', 'country_code': 'en'},
        #         'payload': {'abonent_name': 'Sanya'},
        #     },
        #     'x_idempotency_token: 1',
        #     400,
        #     None,
        # ),
        (
            {
                'personal_phone_id': 'default_phone_id',
                'scenario_name': 'scenario_1',
                'context': {'eater_id': '1337', 'country_code': 'ru'},
                'payload': {'abonent_name': 'Sanya'},
            },
            'x_idempotency_token: 2',
            200,
            1,
        ),
        (
            {
                'personal_phone_id': 'default_phone_id',
                'scenario_name': 'scenario_1',
                'context': {'eater_id': '1337', 'country_code': 'ru'},
                'payload': {'abonent_name': 'Sanya'},
            },
            'x_idempotency_token: 4',
            200,
            4,
        ),
    ],
    ids=[
        '400 wrong input data',
        # '400 unknown country for ivr_flow_id',
        '200 existed token',
        '200 default',
    ],
)
async def test_create_call(
        # ---- fixtures ----
        taxi_eats_robocall,
        pgsql,
        # ---- parameters ----,
        request_body,
        token,
        expected_status_code,
        expected_task_id,
):
    response = await taxi_eats_robocall.post(
        'internal/eats-robocall/v1/create-call',
        headers={'X-Idempotency-Token': token},
        json=request_body,
    )

    assert response.status_code == expected_status_code

    cursor = pgsql['eats_robocall'].cursor()
    cursor.execute(
        'SELECT * from eats_robocall.idempotency_tokens WHERE token = %s',
        (token,),
    )
    if expected_task_id is not None:
        assert list(cursor)[0][1] == expected_task_id
    else:
        assert list(cursor) == []


@pytest.mark.experiments3(filename='scenarios.json')
async def test_stq_create_call_client(
        # ---- fixtures ----
        taxi_eats_robocall,
        stq,
):
    response = await taxi_eats_robocall.post(
        'internal/eats-robocall/v1/create-call',
        headers={'X-Idempotency-Token': 'x_idempotency_token_1000'},
        json={
            'personal_phone_id': 'default_phone_id',
            'scenario_name': 'scenario_1',
            'context': {
                'eater_id': '1337',
                'country_code': 'ru',
                'locale': 'ru',
            },
            'payload': {'abonent_name': 'Sanya'},
        },
    )

    assert response.status_code == 200
    res = stq.eats_robocall_create_call.next_call()

    assert res['queue'] == 'eats_robocall_create_call'
    assert res['id'] == '1'
    assert res['kwargs']['context'] == {
        'eater_id': '1337',
        'payload': {'abonent_name': 'Sanya'},
        'scenario_name': 'scenario_1',
        'country_code': 'ru',
        'locale': 'ru',
    }


@pytest.mark.pgsql('eats_robocall', files=['add_calls.sql'])
@pytest.mark.experiments3(filename='scenarios.json')
@pytest.mark.parametrize(
    'ivr_status_code, expected_status',
    [
        (200, 'success_call_creation'),
        (404, 'telephony_error'),
        (429, 'telephony_error'),
        (500, 'telephony_error'),
    ],
    ids=[
        'default 200',
        'wrong ivr_flow_id',
        'rate-limiter',
        '500 ivr_dispatcher',
    ],
)
async def test_stq_create_call_dispatcher(
        # ---- fixtures ----
        stq_runner,
        mockserver,
        pgsql,
        # ---- parameters ----,
        ivr_status_code,
        expected_status,
):
    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    def _mock_ivr_dispatcher_(request):
        assert request.json['context'] == {
            'payload': {'abonent_name': 'Sanya'},
            'eater_id': '1337',
            'scenario_name': 'scenario_1',
            'country_code': 'ru',
        }
        return mockserver.make_response(status=ivr_status_code)

    await stq_runner.eats_robocall_create_call.call(
        task_id='1',
        args=[],
        kwargs={
            'call_external_id': 'some_id',
            'context': {
                'payload': {'abonent_name': 'Sanya'},
                'eater_id': '1337',
                'scenario_name': 'scenario_1',
                'country_code': 'ru',
            },
            'ivr_flow_id': 'eats_flow',
            'personal_phone_id': 'default_phone_id',
        },
    )

    assert _mock_ivr_dispatcher_.times_called == 1

    cursor = pgsql['eats_robocall'].cursor()
    cursor.execute('SELECT status from eats_robocall.calls WHERE id = 1')
    status = list(cursor)[0][0]
    assert status == expected_status


@pytest.mark.pgsql('eats_robocall', files=['add_calls.sql'])
@pytest.mark.experiments3(filename='scenarios.json')
@pytest.mark.parametrize(
    'ivr_status_code, expected_status', [(200, 'telephony_error')],
)
async def test_stq_create_call_dispatcher_status(
        # ---- fixtures ----
        stq_runner,
        mockserver,
        pgsql,
        # ---- parameters ----,
        ivr_status_code,
        expected_status,
):
    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    def _mock_ivr_dispatcher_(request):
        assert request.json['context'] == {
            'payload': {'abonent_name': 'Sanya'},
            'eater_id': '1337',
            'scenario_name': 'scenario_1',
            'country_code': 'ru',
        }
        return mockserver.make_response(status=ivr_status_code)

    await stq_runner.eats_robocall_create_call.call(
        task_id='1',
        args=[],
        kwargs={
            'call_external_id': 'random_call_external_id3',
            'context': {
                'payload': {'abonent_name': 'Sanya'},
                'eater_id': '1337',
                'scenario_name': 'scenario_1',
                'country_code': 'ru',
            },
            'ivr_flow_id': 'eats_flow',
            'personal_phone_id': 'default_phone_id',
        },
    )

    assert _mock_ivr_dispatcher_.times_called == 0

    cursor = pgsql['eats_robocall'].cursor()
    cursor.execute('SELECT status from eats_robocall.calls WHERE id = 3')
    status = list(cursor)[0][0]
    assert status == expected_status
