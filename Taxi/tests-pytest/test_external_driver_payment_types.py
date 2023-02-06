import pytest

from taxi import config
from taxi.core import arequests
from taxi.external import driver_payment_types
from taxi.internal.dbh import driver_payment_type


@pytest.mark.parametrize('status_code,request_exception', [
    (200, None),
    (404, None),
    (400, None),
    (500, None),
    (200, arequests.ConnectionClosedError('error')),
])
@pytest.inline_callbacks
def test_update_statistics(areq_request, status_code, request_exception):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        assert url.endswith('/service/v1/update-statistics')
        assert kwargs['json'] == {
            'park_id': 'park1',
            'driver_profile_id': 'driver1',
            'order': {
                'id': 'order1',
                'payment_type': 'cash',
                'nearest_zone': 'moscow',
                'travel_time': 10,
                'travel_distance': 20,
            },
        }
        if request_exception is None:
            return areq_request.response(
                status_code,
                body={}
            )
        else:
            raise request_exception

    if request_exception is None and status_code == 200:
        response = yield driver_payment_types.update_statistics(
            'stq', 'park1', 'driver1', 'order1', 'cash', 10, 20, 'moscow',
        )
        assert response is None
    else:
        with pytest.raises(driver_payment_types.RequestError):
            yield driver_payment_types.update_statistics(
                'stq', 'park1', 'driver1', 'order1', 'cash', 10, 20, 'moscow',
            )


@pytest.mark.filldb(orders='auto_compensations')
@pytest.inline_callbacks
def test_update_statistics_old_way():
    yield driver_payment_type.Doc.update_statistics('order1', 'license1', 10,
                                                    10, 'cash', 'moscow')
    doc = yield driver_payment_type.Doc.find_one_by_id('license1')
    assert doc == {
        'order_ids': [
            'order1'
        ],
        '_id': 'license1',
        'enabled': True,
        'enabled_count': 0,
        'payment_type': 'cash',
        'cash': {
            'travel_time': 10,
            'travel_distance': 10
        }
    }
    yield driver_payment_type.Doc.update_statistics(
        'order2',
        'license1',
        10000,
        4000,
        'cash',
        'moscow',
    )
    doc = yield driver_payment_type.Doc.find_one_by_id('license1')
    assert doc['payment_type'] == 'none'
    assert doc['cash'] == {
        'travel_time': 0,
        'travel_distance': 0
    }
    yield config.DRIVER_PAYMENT_TYPE_TRAVEL_LIMITS.save(
        {
            '__default__':
                {
                    'distance': {
                        'cash': 10000,
                        'online': 10000
                    },
                    'time': {
                        'cash': 3600,
                        'online': 3600
                    }
                },
                'zones': {
                    'distance': {
                        'cash': 5,
                        'online': 10000
                    },
                    'time': {
                        'cash': 5,
                        'online': 3600
                    }
                },
                'countries': {}
        }
    )
    yield driver_payment_type.Doc.update_statistics('order1', 'license1', 10,
                                                    10, 'cash', 'moscow')
    doc = yield driver_payment_type.Doc.find_one_by_id('license1')
    assert doc['payment_type'] == 'none'
    assert doc['cash'] == {
        'travel_time': 0,
        'travel_distance': 0
    }
