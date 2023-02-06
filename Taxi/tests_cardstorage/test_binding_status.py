import datetime

import pytest

from tests_cardstorage import common


BINDING_INFO_BODY = {
    'event': 'card_data_received',
    'binding_info': {
        'uid': 'uid',
        'device_id': 'device_id',
        'binding': {
            'type': 'type',
            'id': 'binding_id',
            'number': 'number',
            'service_labels': [],
        },
    },
}


@pytest.mark.config(TVM_ENABLED=True)
@common.tvm_ticket
@pytest.mark.parametrize('tvm, code', [(False, 401), (True, 200)])
async def test_binding_status_access(tvm, code, taxi_cardstorage):
    body = BINDING_INFO_BODY
    headers = {'X-Ya-Service-Ticket': common.MOCK_TICKET if tvm else ''}
    response = await taxi_cardstorage.post(
        'v1/binding_status', json=body, headers=headers,
    )
    assert response.status_code == code


async def test_card_data_received(taxi_cardstorage, mockserver, mongodb):
    response = await taxi_cardstorage.post(
        'v1/binding_status', json=BINDING_INFO_BODY,
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'success'}


async def test_3ds_start(taxi_cardstorage, mockserver, stq, mongodb):
    response = await taxi_cardstorage.post(
        'v1/binding_status',
        json={
            'event': '3ds_start',
            'verification_info': {
                'uid': 'uid',
                'binding_id': 'binding_id1',
                'verification': {
                    'id': 'id',
                    'method': 'method',
                    'status': 'in_progress',
                    'start_ts': '2018-02-07T22:33:09.582Z',
                },
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'success'}

    obj = mongodb.trust_verifications.find_one({'binding_id': 'binding_id1'})
    obj.pop('_id')
    assert obj == {
        'uid': 'uid',
        'binding_id': 'binding_id1',
        'verification_id': 'id',
        'method': 'method',
        'status': 'in_progress',
        'start_ts': datetime.datetime(2018, 2, 7, 22, 33, 9, 582000),
    }
    assert stq.process_card_verification.times_called == 1


@pytest.mark.parametrize(
    'db_status,request_status,expected_status',
    [
        ('success', '3ds_required', 'success'),
        ('3ds_status_received', '3ds_required', '3ds_status_received'),
        ('3ds_required', '3ds_status_received', '3ds_status_received'),
        ('in_progress', '3ds_required', '3ds_required'),
    ],
)
async def test_status_ignore(
        db_status,
        request_status,
        expected_status,
        taxi_cardstorage,
        mockserver,
        mongodb,
):
    mongodb.trust_verifications.update(
        {'binding_id': 'binding_id1'},
        {
            'uid': 'uid',
            'binding_id': 'binding_id1',
            'verification_id': 'id',
            'method': 'method',
            'status': db_status,
            'start_ts': datetime.datetime(2018, 2, 7, 22, 33, 9, 582000),
        },
        upsert=True,
    )
    response = await taxi_cardstorage.post(
        'v1/binding_status',
        json={
            'event': '3ds_start',
            'verification_info': {
                'uid': 'uid',
                'binding_id': 'binding_id1',
                'verification': {
                    'id': 'id',
                    'method': 'method',
                    'status': request_status,
                    'start_ts': '2018-02-07T22:33:09.582Z',
                },
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'success'}

    obj = mongodb.trust_verifications.find_one({'binding_id': 'binding_id1'})
    obj.pop('_id')
    assert obj == {
        'uid': 'uid',
        'binding_id': 'binding_id1',
        'verification_id': 'id',
        'method': 'method',
        'status': expected_status,
        'start_ts': datetime.datetime(2018, 2, 7, 22, 33, 9, 582000),
    }
