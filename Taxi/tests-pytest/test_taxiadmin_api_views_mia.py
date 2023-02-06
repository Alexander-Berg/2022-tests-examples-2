# coding: utf-8
from __future__ import unicode_literals

import datetime
import json

from django import test as django_test
from django.conf import settings as django_settings
from django.test import utils
import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.external import archive
from taxi.util import dates


@pytest.mark.parametrize('data,code', [
    (
        {
            'conditions':
                [
                    {
                        'expression': {
                            'field': 'user_phone',
                            'operator': 'eq',
                            'reference_value': '+7',
                        }
                    },
                    {
                        'sub_conditions': [
                            {
                                'expression': {
                                    'field': 'request_due',
                                    'operator': 'falls_inside',
                                    'reference_value':
                                        '2017-08-22T10:00:00Z/'
                                        '2017-08-23T10:00:00Z',
                                },
                            }
                        ],
                    }
                ],
            'operator': 'and',
        },
        400,
    ),
    (
        {
            'conditions':
                [
                    {
                        'expression': {
                            'field': 'user_phones',
                            'operator': 'eq',
                            'reference_value': '89222222222',
                        }
                    },
                ],
            'operator': 'and',
        },
        406,
    ),
    (
        {
            'conditions':
                [
                    {
                        'operator': 'and',
                        'sub_conditions': [],
                        'expression': {
                            'field': 'user_phone',
                            'operator': 'eq',
                            'reference_value': '89222222222',
                        }
                    },
                ],
            'operator': 'and',
        },
        400,
    ),
    (
        {
              'conditions': [
                    {
                      'expression': {
                        'operator': 'eq',
                        'field': 'user_phone',
                        'reference_value': '+66917194742'
                      }
                },
                {
                  'expression': {
                    'operator': 'falls_inside',
                    'field': 'request_due',
                    'reference_value': '2017-09-18T12:10:07.277392/'
                                       '2018-09-18T12:10:07.277407'
                  }
                },
                {
                  'expression': {
                    'operator': 'falls_inside',
                    'field': 'created',
                    'reference_value': '2018-02-18T00:00:00/'
                                       '2018-09-18T00:00:00'
                  }
                }
          ],
            'operator': 'and',
        },
        200
    ),
    (
        {
              'conditions': [
                    {
                      'expression': {
                        'operator': 'eq',
                        'field': 'user_phone',
                        'reference_value': '86917194742'
                      }
                },
                {
                  'expression': {
                    'operator': 'falls_inside',
                    'field': 'request_due',
                    'reference_value': '2017-09-18T12:10:07.277392/'
                                       '2018-09-18T12:10:07.277407'
                  }
                },
                {
                  'expression': {
                    'operator': 'falls_inside',
                    'field': 'created',
                    'reference_value': '2018-02-18T00:00:00/'
                                       '2018-09-18T00:00:00'
                  }
                }
          ],
            'operator': 'and',
        },
        400
    ),
    (
        {
            'conditions': [
                {
                    'expression': {
                        'operator': 'eq',
                        'field': 'order_source',
                        'reference_value': 'uber'
                    }
                },
            ],
            'operator': 'and',
        },
        200
    ),
])
@pytest.mark.now('2018-09-18 18:04:00+05')
@pytest.mark.asyncenv('blocking')
def test_create_mia_request(data, code):
    url = '/api/mia/queries/'
    request = json.dumps(data)
    response = django_test.Client().post(url, request, 'application/json')
    assert response.status_code == code


@pytest.mark.parametrize('old_request,new_request', [
    (
            {
                'conditions': [
                    {
                        'expression': {
                            'operator': 'eq',
                            'field': 'user_phone',
                            'reference_value': '+66917194742'
                        }
                    },
                    {
                        'expression': {
                            'operator': 'eq',
                            'field': 'order_source',
                            'reference_value': 'uber'
                        }
                    },
                    {
                        'expression': {
                            'operator': 'regex',
                            'field': 'source_address',
                            'reference_value': 'abc.+'
                        }
                    },
                    {
                        'expression': {
                            'operator': 'falls_inside',
                            'field': 'request_due',
                            'reference_value': '2017-09-18T12:10:07.277392/'
                                               '2018-09-18T12:10:07.277407'
                        }
                    },
                    {
                        'expression': {
                            'operator': 'falls_inside',
                            'field': 'created',
                            'reference_value': '2018-02-18T00:00:00/'
                                               '2018-09-18T00:00:00'
                        }
                    },
                ],
                'operator': 'and',
            },
            {
                'exact': {
                    'order_source': 'uber',
                    'user_phone': '+66917194742'
                },
                'period': {
                    'created': {
                        'from': '2018-02-18T00:00:00',
                        'to': '2018-09-18T00:00:00'
                    },
                    'request_due': {
                        'from': '2017-09-18T12:10:07.277392',
                        'to': '2018-09-18T12:10:07.277407'
                    }
                },
                'regex': {
                    'source_address': 'abc.+'
                }
            }
    ),
])
@pytest.mark.now('2018-09-18 18:04:00+05')
@pytest.mark.config(MIA_SEND_TO_NEW_SERVICE=True)
@pytest.mark.asyncenv('blocking')
def test_create_new_mia_request(old_request, new_request, patch):
    sent_request = []

    @patch('taxiadmin.api.views.mia._send_request_to_new_mia')
    @async.inline_callbacks
    def _send_request_to_new_mia(r, log_extra):
        sent_request.append(r)
        yield async.return_value({'id': '1'})

    url = '/api/mia/queries/'
    request = json.dumps(old_request)
    response = django_test.Client().post(url, request, 'application/json')
    assert response.status_code == 200
    new_request['check_all_candidates'] = True
    assert sent_request[0] == new_request
    new_request['check_all_candidates'] = False
    assert sent_request[1] == new_request


@pytest.mark.parametrize('data,expected_ids', [
    (
        {
            'created_by': 'test_user',
        },
        [0, 2],
    ),
    (
        {
            'range': {
                'newer_than': '7d9c477b25094e399d7ac67c95bcc747',
            }
        },
        [1],
    ),
    (
        {
            'range': {
                'older_than': '34573655hhf94e399d7ac67c95bcc747',
            }
        },
        [0, 2],
    ),
    (
        {
            'limit': 2,
        },
        [0, 1],
    )
])
@pytest.mark.asyncenv('blocking')
def test_list_mia_requests(data, expected_ids):
    all_query_results = [
        {
            'id': '7d9c477b25094e399d7ac67c95bcc747',
            'conditions': [{
                'expression': {
                    'field': 'user_phone',
                    'operator': 'eq',
                    'reference_value': '89222222222',
                }},
                {
                    'operator': 'or',
                    'sub_conditions': [{
                        'expression': {
                            'field': 'request_due',
                            'operator': 'falls_inside',
                            'reference_value': '2017-08-10T10:00:00Z/'
                                               '2017-08-11T10:00:00Z'
                        }},
                        {
                            'expression': {
                                'field': 'request_due',
                                'operator': 'falls_inside',
                                'reference_value': '2017-08-22T10:00:00Z/'
                                                   '2017-08-23T10:00:00Z'
                            }
                        }
                    ]
                }
            ],
            'created_by': 'test_user',
            'created_time': '2017-08-25T14:41:00+0300',
            'operator': 'and',
            'result': {
                'started_time': '2017-08-25T14:49:00+0300',
                'status': 'in_progress',
            },
            'updated_time': '2017-08-25T15:41:00+0300'
        },
        {
            'id': '34573655hhf94e399d7ac67c95bcc747',
            'conditions': [{
                'expression': {
                    'field': 'user_phone',
                    'operator': 'eq',
                    'reference_value': '89222222222'}
              },
              {
                'operator': 'or',
                'sub_conditions': [{
                    'expression': {
                        'field': 'request_due',
                        'operator': 'falls_inside',
                        'reference_value': '2017-08-10T10:00:00Z/'
                                           '2017-08-11T10:00:00Z'}
                    },
                    {
                        'expression': {
                            'field': 'request_due',
                            'operator': 'falls_inside',
                            'reference_value': '2017-08-22T10:00:00Z/'
                                               '2017-08-23T10:00:00Z'
                        }
                    }
                ]}
            ],
            'created_by': 'not_test_user',
            'created_time': '2017-08-25T14:41:00+0300',
            'operator': 'and',
            'updated_time': '2017-08-25T15:41:00+0300',
            'result': {
                'started_time': '2017-08-25T14:49:00+0300',
                'status': 'failed',
                'error': 'Test Error',
                'finished_time': '2017-08-25T15:41:00+0300',
            },
        },
        {
            'id': '57t476347h4e399d7ac67c95bcc747',
            'conditions': [{
                    'expression': {
                        'field': 'user_phone',
                        'operator': 'eq',
                        'reference_value': '87777222222'
                    }
                },
                {
                    'operator': 'or',
                    'sub_conditions': [{
                            'expression': {
                                'field': 'request_due',
                                'operator': 'falls_inside',
                                'reference_value': '2017-06-10T10:00:00Z/'
                                                   '2017-06-11T10:00:00Z',
                        }},
                        {
                            'expression': {
                                'field': 'request_due',
                                'operator': 'falls_inside',
                                'reference_value': '2017-07-22T10:00:00Z/'
                                                   '2017-07-23T10:00:00Z'
                            }
                        }
                    ]
                }
            ],
            'result': {
                'finished_time': '2017-08-09T15:41:00+0300',
                'result_url': '598/c94a13d-rf7rfyhr-b4b63e18f810',
                'started_time': '2017-08-08T18:49:00+0300',
                'status': 'succeeded',
            },
            'created_by': 'test_user',
            'created_time': '2017-08-08T14:41:00+0300',
            'operator': 'and',
            'updated_time': '2017-08-09T15:41:00+0300'
        }
    ]
    url = '/api/mia/queries/list/'
    request = json.dumps(data)
    response = django_test.Client().post(url, request, 'application/json')
    assert response.status_code == 200
    expected_queries = {
        all_query_results[ind]['id']: all_query_results[ind]
        for ind in expected_ids
    }
    results = json.loads(response.content)
    queries = {
        result['id']: result
        for result in results['queries']
    }
    assert expected_queries == queries


@pytest.mark.parametrize('query_id,code,expected_result', [
    (
        '34573655hhf94e399d7ac67c95bcc747', 200,
        {
            'id': '34573655hhf94e399d7ac67c95bcc747',
            'conditions': [{
                'expression': {
                    'field': 'user_phone',
                    'operator': 'eq',
                    'reference_value': '89222222222'}
              },
              {
                'operator': 'or',
                'sub_conditions': [{
                    'expression': {
                        'field': 'request_due',
                        'operator': 'falls_inside',
                        'reference_value': '2017-08-10T10:00:00Z/'
                                           '2017-08-11T10:00:00Z'}
                    },
                    {
                        'expression': {
                            'field': 'request_due',
                            'operator': 'falls_inside',
                            'reference_value': '2017-08-22T10:00:00Z/'
                                               '2017-08-23T10:00:00Z'
                        }
                    }
                ]}
            ],
            'created_by': 'not_test_user',
            'created_time': '2017-08-25T14:41:00+0300',
            'operator': 'and',
            'updated_time': '2017-08-25T15:41:00+0300',
            'result': {
                'started_time': '2017-08-25T14:49:00+0300',
                'status': 'failed',
                'error': 'Test Error',
                'finished_time': '2017-08-25T15:41:00+0300',
            },
        },
    ),
    ('non_existing_id', 404, None),
])
@pytest.mark.asyncenv('blocking')
def test_get_mia_request(query_id, code, expected_result):
    url = '/api/mia/queries/{}/'.format(query_id)
    response = django_test.Client().get(url)
    assert response.status_code == code
    if code == 200:
        result = json.loads(response.content)
        assert result == expected_result


@utils.override_settings(BLACKBOX_AUTH=True)
@pytest.mark.asyncenv('blocking')
def test_queries_list_external_auth_success():
    response = django_test.Client().post(
        '/api/mia/queries/list/', '{}', 'application/json',
        HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY
    )
    assert response.status_code == 200, response.content
    result = json.loads(response.content)
    assert sorted(result.keys()) == ['queries', 'total']
    assert result['total'] == len(result['queries']) == 3


@utils.override_settings(BLACKBOX_AUTH=True)
@pytest.mark.asyncenv('blocking')
def test_queries_list_external_auth_fail():
    response = django_test.Client().post(
        '/api/mia/queries/list/', '{}', 'application/json',
        HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY + '_'
    )
    assert response.status_code == 401


@utils.override_settings(BLACKBOX_AUTH=True)
@pytest.mark.asyncenv('blocking')
def test_check_user_by_phone():
    response = django_test.Client().get(
        '/api/mia/check_user/?phone=%2B79001112233&type=yandex',
        HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY
    )
    assert response.status_code == 200
    created = dates.parse_timestring(
        json.loads(response.content)['created']
    )
    assert created == datetime.datetime(2018, 4, 1, 0, 0, 0)

    response = django_test.Client().get(
        '/api/mia/check_user/?phone=%2B79001112233&type=uber',
        HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY
    )
    assert response.status_code == 404

    response = django_test.Client().get(
        '/api/mia/check_user/?phone=89004445566&type=uber',
        HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY
    )
    assert response.status_code == 200
    created = dates.parse_timestring(
        json.loads(response.content)['created']
    )
    assert created == datetime.datetime(2018, 3, 1, 0, 0, 0)

    response = django_test.Client().get(
        '/api/mia/check_user/?phone=89007778899&type=yandex',
        HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY
    )
    assert response.status_code == 200
    created = dates.parse_timestring(
        json.loads(response.content)['created']
    )
    assert created == datetime.datetime(2014, 6, 26, 0, 0, 0)

    response = django_test.Client().get(
        '/api/mia/check_user/?phone=%2B79000000000&type=yandex',
        HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY
    )
    assert response.status_code == 404

    response = django_test.Client().get(
        '/api/mia/check_user/?phone=%2B790011122330&type=yandex',
        HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY + '_'
    )
    assert response.status_code == 401

    response = django_test.Client().get(
        '/api/mia/check_user/?phone=%2B66917194742&type=yandex',
        HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY
    )

    assert response.status_code == 200

    response = django_test.Client().get(
        '/api/mia/check_user/?phone=+66917194742&type=yandex',
        HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY
    )

    assert response.status_code == 404


class TestCreateQuery(object):
    def setup(self):
        self.bb_auth_orig = django_settings.BLACKBOX_AUTH
        django_settings.BLACKBOX_AUTH = True

    @pytest.mark.asyncenv('blocking')
    @pytest.inline_callbacks
    def test_auth_external_login_None(self, patch):
        response = django_test.Client().post(
            '/api/mia/queries/',
            json.dumps({'conditions': [], 'operator': 'and'}),
            'application/json',
            HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY
        )
        assert response.status_code == 200, response.content

        result = json.loads(response.content)
        assert result.keys() == ['id']

        query_id = result['id']
        query = (yield db.mia_requests.find({'_id': query_id}).run())[0]
        assert query['created_by'] is None

        response = django_test.Client().get(
            '/api/mia/queries/{}/'.format(query_id),
            HTTP_X_YATAXI_API_KEY=settings.MIA_ADMIN_AUTH_KEY
        )
        assert response.status_code == 200, response.content
        result = json.loads(response.content)
        assert result['created_by'] is None

    def teardown(self):
        django_settings.BLACKBOX_AUTH = self.bb_auth_orig


@pytest.mark.parametrize(
    'order_id,expected_code,expected_response,expected_time_range',
    [
        (
            'no_such_order',
            404,
            {
                'status': 'error',
                'code': 'order_not_found',
                'message': 'Order no_such_order not found',
            },
            # no calls to get_driver_track
            None,
        ),
        (
            'order_without_route_without_track',
            200,
            {'route': [{'lon': 10.1, 'lat': 20.2}], 'track': []},
            (1529193600, 1529280000),
        ),
        (
            'order_with_route_without_track',
            200,
            {
                'route': [
                    {'lon': 10.1, 'lat': 20.2},
                    {'lon': 30.3, 'lat': 40.4},
                ],
                'track': [],
            },
            (1529193600, 1529280000),
        ),
        (
            'order_with_route_with_track',
            200,
            {
                'route': [
                    {'lon': 10.1, 'lat': 20.2},
                    {'lon': 30.3, 'lat': 40.4}
                ],
                'track': [
                    {
                        'lon': 10.1,
                        'lat': 20.2,
                        'bearing': -1,
                        'timestamp': 1529096169,
                    },
                    {
                        'lon': 30.3,
                        'lat': 40.4,
                        'bearing': -1,
                        'timestamp': 1529096169,
                    },
                ],
            },
            (1529193600, 1529280000),
        ),
        (
            'order_with_3_route_points_without_track',
            200,
            {
                'route': [
                    {'lon': 10.1, 'lat': 20.2},
                    {'lon': 30.3, 'lat': 40.4},
                    {'lon': 50.5, 'lat': 60.6}
                ],
                'track': [],
            },
            (1529193600, 1529280000),
        ),
        (
            'pool_order',
            200,
            {
                'route': [
                    {'lon': 10.1, 'lat': 20.2},
                    {'lon': 30.3, 'lat': 40.4},
                    {'lon': 50.5, 'lat': 60.6}
                ],
                'track': [],
            },
            # no calls to get_driver_track
            None,
        ),
        (
            'order_without_source',
            200,
            {
                'route': [],
                'track': [],
            },
            (1529193600, 1529280000),
        )
    ]
)
@pytest.mark.config(MIA_ORDER_TRACK_TIME_RANGE_MARGIN=0)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_order_track(
        patch, load, order_id, expected_code,
        expected_response, expected_time_range):
    # Responses by order_id
    geotracks_data = json.loads(load('geotracks_data.json'))

    @patch('taxi.external.archive.get_order_proc_by_id')
    @async.inline_callbacks
    def get_order_proc_by_id(order_id, lookup_yt=True, src_tvm_service=None,
                             log_extra=None):
        yield
        raise archive.NotFoundError

    @patch('taxi.external.geotracks.get_driver_track')
    @async.inline_callbacks
    def get_driver_track(
            driver_id, db, start_time, end_time, tvm_src_service,
            verbose=False, log_extra=None):
        yield async.return_value(geotracks_data[order_id])

    response = yield django_test.Client().get(
        '/api/mia/get_order_track/?order_id={0}'.format(order_id)
    )
    assert response.status_code == expected_code
    response_data = json.loads(response.content)
    assert response_data == expected_response
    if expected_code == 200:
        if expected_time_range is None:
            assert not get_driver_track.calls
        else:
            start_time, end_time = expected_time_range
            call = get_driver_track.calls[0]
            assert call['kwargs']['start_time'] == start_time
            assert call['kwargs']['end_time'] == end_time


@pytest.mark.parametrize('query', ['', '?order_id=foobar&energy=mc2'])
@pytest.mark.config(MIA_ORDER_TRACK_TIME_RANGE_MARGIN=0)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_order_track_validation(patch, query):

    @patch('taxi.external.archive.get_order_proc_by_id')
    @async.inline_callbacks
    def get_order_proc_by_id(order_id, src_tvm_service=None, log_extra=None):
        yield
        raise archive.NotFoundError

    @patch('taxi.external.geotracks.get_driver_track')
    @async.inline_callbacks
    def get_driver_track(
            driver_id, db, start_time, end_time, tvm_src_service,
            verbose=False, log_extra=None):
        yield async.return_value({'track': []})

    response = yield django_test.Client().get(
        '/api/mia/get_order_track/' + query
    )
    assert response.status_code == 400
