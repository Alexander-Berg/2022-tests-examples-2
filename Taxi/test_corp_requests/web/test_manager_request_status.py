import datetime

import pytest


HEADERS = {'X-Yandex-Login': 'test_login', 'X-Yandex-UID': 'test_uid'}


@pytest.mark.config(
    CORP_MANAGER_REQUEST_CHANGE_STATUS_SLUG_SERVICES={
        '__default__': 'SLUG',
        'cargo': 'cargoSLUG',
    },
)
@pytest.mark.parametrize(
    ['request_id', 'request_params', 'expected_db'],
    [
        (
            'request_pending',
            {'status': 'accepting'},
            {
                '_id': 'request_pending',
                'additional_information': 'r2_17',
                'bank_account_number': 'r2_12',
                'bank_bic': 'r2_11',
                'company_tin_id': 'tin_pd_id2',
                'contacts': [
                    {
                        'email_id': 'lol_email_pd_id',
                        'name': 'r2_8',
                        'phone_id': 'phone_pd_id2',
                    },
                    {
                        'email_id': 'lol_email_pd_id',
                        'name': 'r2_18',
                        'phone_id': 'phone_pd_id2',
                    },
                ],
                'contract_type': 'prepaid',
                'created': datetime.datetime(2000, 1, 2, 0, 0),
                'desired_button_name': 'r2_16',
                'enterprise_name_full': 'r2_5',
                'enterprise_name_short': 'r2_4',
                'final_status_manager_login': 'test_login',
                'legal_address': '6;r2_6',
                'mailing_address': '7;r2_7',
                'manager_login': 'r2_1',
                'signer_duly_authorized': 'charter',
                'signer_gender': 'female',
                'signer_name': 'r2_13',
                'signer_position': 'r2_signer_position',
                'st_link': 'r2_15',
                'status': 'accepting',
                'country': 'rus',
                'kbe': '1',
                'city': 'Москва',
                'service': 'cargo',
            },
        ),
        (
            'request_pending',
            {'status': 'rejected', 'reason': 'so bad'},
            {
                '_id': 'request_pending',
                'additional_information': 'r2_17',
                'bank_account_number': 'r2_12',
                'bank_bic': 'r2_11',
                'company_tin_id': 'tin_pd_id2',
                'contacts': [
                    {
                        'email_id': 'lol_email_pd_id',
                        'name': 'r2_8',
                        'phone_id': 'phone_pd_id2',
                    },
                    {
                        'email_id': 'lol_email_pd_id',
                        'name': 'r2_18',
                        'phone_id': 'phone_pd_id2',
                    },
                ],
                'contract_type': 'prepaid',
                'created': datetime.datetime(2000, 1, 2, 0, 0),
                'desired_button_name': 'r2_16',
                'enterprise_name_full': 'r2_5',
                'enterprise_name_short': 'r2_4',
                'final_status_manager_login': 'test_login',
                'legal_address': '6;r2_6',
                'mailing_address': '7;r2_7',
                'manager_login': 'r2_1',
                'signer_duly_authorized': 'charter',
                'signer_gender': 'female',
                'signer_name': 'r2_13',
                'signer_position': 'r2_signer_position',
                'st_link': 'r2_15',
                'status': 'rejected',
                'country': 'rus',
                'kbe': '1',
                'city': 'Москва',
                'reason': 'so bad',
                'service': 'cargo',
            },
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-requests'},
        {'dst': 'stq-agent', 'src': 'corp-requests'},
    ],
)
async def test_manager_requests_status_ok(
        taxi_corp_requests_web,
        mockserver,
        mock_personal,
        mock_mds,
        mock_sender,
        db,
        request_id,
        request_params,
        expected_db,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue>\w+)', regex=True,
    )
    def _stq_agent_put_task(request, queue):
        pass

    response = await taxi_corp_requests_web.post(
        '/v1/manager-requests/status/update',
        params={'request_id': request_id},
        json=request_params,
        headers=HEADERS,
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    db_item = await db.corp_manager_requests.find_one(
        {'_id': request_id}, projection={'updated': 0},
    )
    assert db_item.pop('final_status_date')
    if request_params['status'] == 'accepting':
        task = db_item.pop('tasks')[0]
        assert set(task.keys()) == {'task_id', 'datetime'}

    assert db_item == expected_db

    assert _stq_agent_put_task.times_called == 1
    stq_call = _stq_agent_put_task.next_call()

    if request_params['status'] == 'accepting':
        assert stq_call['queue'] == 'corp_accept_manager_request'
    else:
        assert stq_call['queue'] == 'corp_notices_process_event'
        assert stq_call['request'].json['kwargs'] == {
            'event_name': 'ManagerRequestStatusChanged',
            'data': {
                'request_id': expected_db['_id'],
                'old': {'status': 'pending'},
                'new': {
                    'status': 'rejected',
                    'reason': request_params['reason'],
                },
            },
        }


@pytest.mark.parametrize(
    ['request_id', 'request_params', 'expected_result'],
    [
        (
            'request_accepted',
            {'status': 'accepting'},
            {
                'code': 'invalid-status-transition',
                'details': {},
                'message': 'invalid status transition',
            },
        ),
        (
            'bad_request',
            {'status': 'accepting'},
            {
                'code': 'mailing_address: bad address format',
                'details': {},
                'message': 'mailing_address: bad address format',
            },
        ),
        (
            'not_found',
            {'status': 'accepting'},
            {
                'code': 'manager-request-not-found',
                'details': {},
                'message': 'manager request not found',
            },
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-requests'},
        {'dst': 'stq-agent', 'src': 'corp-requests'},
    ],
)
async def test_manager_requests_status_fail(
        taxi_corp_requests_web, request_id, request_params, expected_result,
):
    response = await taxi_corp_requests_web.post(
        '/v1/manager-requests/status/update',
        params={'request_id': request_id},
        json=request_params,
        headers=HEADERS,
    )

    response_json = await response.json()
    assert response_json == expected_result
