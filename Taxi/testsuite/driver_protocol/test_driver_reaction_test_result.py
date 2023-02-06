from bson import objectid
import pytest


@pytest.mark.config(SCHULTE_RESULT_TABLE_COUNT_LIMIT=1)
def test_simple(taxi_driver_protocol, db, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.post(
        'driver/reaction_test_result?db=1488&session=qwerty',
        {
            'id': '543eac8978f3c2a8d7983ccc',
            'type': 'schulte',
            'results': [
                {
                    'total_time_ms': 40000,
                    'status': 'success',
                    'clicks': [{'is_hit': True, 'delay_ms': 918}],
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {'passed': True}
    obj = db.reaction_tests.find_one(
        {'_id': objectid.ObjectId('543eac8978f3c2a8d7983ccc')},
    )
    obj.pop('updated')
    assert obj == {
        '_id': objectid.ObjectId('543eac8978f3c2a8d7983ccc'),
        'type': 'schulte',
        'passed': True,
        'unique_driver_id': '543eac8978f3c2a8d7983111',
        'results': [
            {
                'total_time_ms': 40000,
                'status': 'success',
                'clicks': [{'is_hit': True, 'delay_ms': 918}],
            },
        ],
    }


def test_negative(taxi_driver_protocol, db, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.post(
        'driver/reaction_test_result?db=1488&session=qwerty',
        {
            'id': '543eac8978f3c2a8d7983ccd',
            'type': 'schulte',
            'results': [
                {
                    'total_time_ms': 60000,
                    'status': 'success',
                    'clicks': [{'is_hit': True, 'delay_ms': 918}],
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {'passed': False}
    obj = db.reaction_tests.find_one(
        {'_id': objectid.ObjectId('543eac8978f3c2a8d7983ccd')},
    )
    obj.pop('updated')
    assert obj == {
        '_id': objectid.ObjectId('543eac8978f3c2a8d7983ccd'),
        'type': 'schulte',
        'passed': False,
        'unique_driver_id': '543eac8978f3c2a8d7983111',
        'results': [
            {
                'total_time_ms': 60000,
                'status': 'success',
                'clicks': [{'is_hit': True, 'delay_ms': 918}],
            },
        ],
    }


@pytest.mark.parametrize(
    'test_id,test_type,status,time',
    [
        ('invalid', 'schulte', 'success', 15),
        ('543eac8978f3c2a8d7983ccc', 'invalid', 'success', 15),
        ('543eac8978f3c2a8d7983ccc', 'schulte', 'invalid', 15),
        ('543eac8978f3c2a8d7983ccc', 'schulte', 'success', -15),
        ([], 'schulte', 'success', 15),
        ('543eac8978f3c2a8d7983ccc', -1, 'success', 15),
        ('543eac8978f3c2a8d7983ccc', 'schulte', 15, 15),
        ('543eac8978f3c2a8d7983ccc', 'schulte', 'success', '15'),
    ],
)
def test_400(
        taxi_driver_protocol,
        test_id,
        test_type,
        status,
        time,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.post(
        'driver/reaction_test_result?db=1488&session=qwerty',
        {
            'id': test_id,
            'type': test_type,
            'results': [
                {
                    'status': status,
                    'total_time_ms': time,
                    'clicks': [{'is_hit': True, 'delay_ms': 918}],
                },
            ],
        },
    )
    assert response.status_code == 400
