import pytest

SAVE_FEEDBACK_URL = '/cc/v1/callcenter-qa/v1/feedback/save'


@pytest.mark.now('2021-12-31T11:00:00.00Z')
@pytest.mark.config(CALLCENTER_QA_FEEDBACK_SETTINGS={'ServerError': {}})
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_data'],
    (
        pytest.param(
            'request_1.json',
            200,
            (
                'call_id_1',
                'commutation_test',
                'call_guid_1',
                'test_uid',
                'ServerError',
                {
                    'binary_data': [
                        {'mds_link': 'image.link', 'type': 'image'},
                        {'mds_link': 'sip_log.link', 'type': 'sip_log'},
                    ],
                },
            ),
            id='simple_request',
        ),
        pytest.param(
            'request_2.json',
            400,
            {
                'message': 'Undefined feedback type: UndefinedError',
                'code': 'undefined_feedback_type',
            },
            id='undefined_feedback',
        ),
    ),
)
async def test_base_save_feedback(
        taxi_callcenter_qa,
        request_body,
        expected_status,
        expected_data,
        load_json,
        pgsql,
        mockserver,
):
    response = await taxi_callcenter_qa.post(
        SAVE_FEEDBACK_URL,
        json=load_json(request_body),
        headers={'X-Yandex-UID': 'test_uid'},
    )
    assert response.status_code == expected_status

    if expected_status == 200:
        cursor = pgsql['callcenter_qa'].cursor()
        cursor.execute(
            'SELECT call_id, commutation_id, call_guid, '
            'yandex_uid, type, binary_data'
            ' FROM callcenter_qa.feedbacks',
        )
        assert cursor.fetchall()[0] == expected_data
        cursor.close()
    else:
        assert response.json() == expected_data


@pytest.mark.now('2021-12-31T11:00:00.00Z')
@pytest.mark.config(CALLCENTER_QA_FEEDBACK_SETTINGS={'ServerError': {}})
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_response'],
    (
        pytest.param(
            'request_1.json',
            409,
            {
                'message': 'Feedback with id id1 already exists',
                'code': 'entry_already_exists',
            },
            id='entry_already_exists',
        ),
    ),
)
@pytest.mark.pgsql('callcenter_qa', files=['insert_feedback.sql'])
async def test_entry_already_exists(
        taxi_callcenter_qa,
        request_body,
        expected_status,
        expected_response,
        load_json,
        pgsql,
        mockserver,
):
    response = await taxi_callcenter_qa.post(
        SAVE_FEEDBACK_URL,
        json=load_json(request_body),
        headers={'X-Yandex-UID': 'test_uid'},
    )
    assert response.status_code == expected_status

    assert response.json() == expected_response
