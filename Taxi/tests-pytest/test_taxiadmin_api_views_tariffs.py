import datetime
import json
from collections import namedtuple

from bson import json_util
from django import test as django_test
from django.core import urlresolvers
import pytest

from taxi.core import async, db
from taxi.external import agglomerations
from taxi.internal import admin_restrictions
from taxi.internal import dbh
from taxi.internal.dbh import tariffs
from taxiadmin import tariff_checks
from taxiadmin.api.views import tariffs as tariffs_views

import helpers


@pytest.fixture
def extract_log(load):
    def _extract_func(filename):
        log = json_util.loads(load(filename))
        log['timestamp'] = log['timestamp'].replace(
            tzinfo=None
        )
        return log
    return _extract_func


DEFAULT_CONFIG = {
    admin_restrictions.COUNTRY_ACCESS_CONFIG_NAME: {
        'rus': {
            'logins': [
                'karachevda',
            ],
        },
        'kaz': {
            'logins': [
                'karachevda',
            ],
        },
    },
    admin_restrictions.CATEGORY_ACCESS_CONFIG_NAME: {
        'passenger_basic': {
            'logins': [
                'karachevda',
            ],
        }
    }
}

CATEGORY_PRESET_CONFIG = {
  "passenger_basic": {
    "__default__": [
      "vip",
    ],
  },
}


def _patch_internals(patch, config):

    @patch('taxi.external.experiments3.get_config_values')
    @async.inline_callbacks
    def _get_experiments(consumer, config_name, *args, **kwargs):
        yield
        if config_name in config:
            resp = [
                admin_restrictions.experiments3.ExperimentsValue(
                    config_name, config[config_name],
                ),
            ]
        else:
            resp = []
        async.return_value(resp)


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ALL_CATEGORIES=['econom', 'vip'])
@pytest.mark.parametrize('request_tariff_type', ['vip', 'pool'])
def test_using_wrong_tariff_category(request_tariff_type, patch):

    @patch('taxiadmin.audit.check_taxirate')
    @async.inline_callbacks
    def check_taxirate(ticket_key, login, check_author=False):
        yield async.return_value()

    categories = [{
        'category_name': request_tariff_type,
        'category_type': 'application',
        'time_from': '00:00',
        'time_to': '23:59',
        'name_key': 'interval.24h',
        'day_type': 2,
        'currency': 'RUR',
        'minimal': 42,
        'paid_cancel_fix': 30,
        'add_minimal_to_paid_cancel': False
    }]

    response = django_test.Client().post(
        '/api/set_tariff/moscow/', json.dumps(
            {
                'activation_zone': 'moscow',
                'home_zone': 'moscow',
                'categories': categories,
                'ticket': 'TAXIRATE-0001',
            }
        ),
        content_type='application/json')

    # 406 because of checking for existing zone.
    assert response.status_code == (
        406 if request_tariff_type == 'vip' else 400
    )


@pytest.fixture
def tariff(load):
    return json.loads(load('tariffs.json'))


@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_negative_price(tariff):

    with pytest.raises(tariff_checks.SpecialTaximeterIntervalValidationError):
        tariff['categories'][0]['special_taximeters'][0]['price']['time_price_intervals'][0]['price'] = -1
        tariff_doc = tariffs.Doc._from_json(tariff)
        yield tariff_checks._check_price_intervals(tariff_doc)


@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_price_intervals_with_intersection(tariff):

    with pytest.raises(tariff_checks.SpecialTaximeterIntervalValidationError):
        tariff['categories'][0]['special_taximeters'][0]['price']['time_price_intervals'][1]['begin'] = 20
        tariff_doc = tariffs.Doc._from_json(tariff)
        yield tariff_checks._check_price_intervals(tariff_doc)


@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_price_intervals_bad_len(tariff):

    with pytest.raises(tariff_checks.SpecialTaximeterIntervalValidationError):
        tariff['categories'][0]['special_taximeters'][0]['price']['time_price_intervals'][0]['end'] = 2
        tariff_doc = tariffs.Doc._from_json(tariff)
        yield tariff_checks._check_price_intervals(tariff_doc)


@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_price_intervals_validation_error_context_on_special_taximeters(tariff):
    tariff['categories'][0]['special_taximeters'][0]['price']['time_price_intervals'][0]['end'] = 2
    tariff_doc = tariffs.Doc._from_json(tariff)
    try:
        yield tariff_checks._check_price_intervals(tariff_doc)
    except tariff_checks.SpecialTaximeterIntervalValidationError as exc:
        msg = exc.msg()
        assert msg.startswith(
            '[category: business '
            '| day type: interval.dayoff '
            '| day interval: 00:00-23:59 '
            '| ride in moscow zone '
            '| tariffication type: time] '
            'invalid interval'
        )
        changed_interval = tariff['categories'][0]['special_taximeters'][0]['price']['time_price_intervals'][0]
        assert (json.dumps(changed_interval, sort_keys=True) in msg)
    else:
        assert False, 'Check not failed. Expect SpecialTaximeterIntervalValidationError exception'


@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_price_intervals_validation_error_context_on_requirement_special_taximeters(tariff):
    special_taximeters = tariff['categories'][0]['special_taximeters']
    special_taximeters[0]['price']['time_price_intervals'][0]['end'] = 2
    tariff['categories'][0]['summable_requirements'][0]['price'] = {
        'special_taximeters': special_taximeters
    }
    tariff_doc = tariffs.Doc._from_json(tariff)
    try:
        yield tariff_checks._check_category_requirements(
            tariff_doc.categories[0], tariff_doc.home_zone
        )
    except tariff_checks.RequirementSpecialTaximeterIntervalValidationError as exc:
        msg = exc.msg()
        assert msg.startswith(
            '[category: business '
            '| day type: interval.dayoff '
            '| day interval: 00:00-23:59 '
            '| ride in moscow zone for animaltransport requirement '
            '| tariffication type: time] '
            'invalid interval'
        )
        changed_interval = special_taximeters[0]['price']['time_price_intervals'][0]
        assert (json.dumps(changed_interval, sort_keys=True) in msg)
    else:
        assert False, 'Check not failed. Expect SpecialTaximeterIntervalValidationError exception'


@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_price_intervals_validation_error_context_on_zonal_prices(tariff):
    tariff['categories'][0]['zonal_prices'][0]['price']['distance_price_intervals'][0]['end'] = 6
    tariff['categories'][0]['zonal_prices'][0]['price']['distance_price_intervals'].append({
        'price': 10,
        'begin': 5
    })
    tariff_doc = tariffs.Doc._from_json(tariff)
    try:
        yield tariff_checks._check_price_intervals(tariff_doc)
    except tariff_checks.ZonalIntervalValidationError as exc:
        msg = exc.msg()
        assert msg == ('[category: business '
                       '| day type: interval.dayoff '
                       '| day interval: 00:00-23:59 '
                       '| ride from moscow to svo '
                       '| tariffication type: distance] '
                       'intervals intersection: {..., "end": 6} & {"begin": 5,...}')
    else:
        assert False, 'Check not failed. Expect ZonalIntervalValidationError exception'


@pytest.mark.config(
    PRICE_INTERVALS_GAP_VALIDATION={
        '__default__': False,
        'moscow': True
    }
)
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_price_intervals_with_gap(tariff):

    with pytest.raises(tariff_checks.SpecialTaximeterIntervalValidationError):
        tariff['categories'][0]['special_taximeters'][0]['price']['time_price_intervals'][1]['begin'] = 30
        tariff_doc = tariffs.Doc._from_json(tariff)
        yield tariff_checks._check_price_intervals(tariff_doc)


@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_price_interval_with_gap_disabled_check(tariff):
    """
    validation disabled by default in config
    test must not fail
    """
    tariff['categories'][0]['special_taximeters'][0]['price']['time_price_intervals'][1]['begin'] = 30
    tariff_doc = tariffs.Doc._from_json(tariff)
    yield tariff_checks._check_price_intervals(tariff_doc)


@pytest.mark.parametrize(
    'home_zone,expected_paid_cancel_fix,expected_add_minimal_to_paid_cancel', [
        ('moscow', 30, False),
        ('linyovo', 0, True)
    ]
)
@pytest.mark.filldb(tariffs='get')
@pytest.mark.asyncenv('blocking')
def test_get_tariff_paid_cancel_fix(
        home_zone, expected_paid_cancel_fix, expected_add_minimal_to_paid_cancel
):
    response = django_test.Client().get(
        '/api/tariff/{}/'.format(home_zone)
    )
    assert response.status_code == 200

    data = json.loads(response.content)
    category = data['categories'][0]

    assert category['paid_cancel_fix'] == expected_paid_cancel_fix
    assert category['add_minimal_to_paid_cancel'] == (
            expected_add_minimal_to_paid_cancel
    )


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
@pytest.mark.disable_territories_api_mock
@pytest.mark.translations([
    ('tariff', 'interval.24h', 'en', 'allday'),
    ('tariff', 'currency.rub', 'en', 'ruble'),
    ('geoareas', 'moscow', 'en', 'Moscow'),
    ('tariff', 'interval.24h', 'ru', 'allday'),
    ('tariff', 'currency.rub', 'ru', 'ruble'),
    ('geoareas', 'moscow', 'ru', 'Moscow'),
])
def test_set_tariff_x_ya_request_id(areq_request, patch):
    uuid = 'test_uuid'

    @patch('taxiadmin.audit.check_taxirate')
    @async.inline_callbacks
    def check_taxirate(ticket_key, login, check_author=False):
        yield async.return_value()

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = namedtuple('uuid4', 'hex')
        return uuid4_(uuid)

    @areq_request
    def countries(*args, **kwargs):
        assert kwargs['headers']['X-YaRequestId'] == uuid
        return areq_request.response(200, body=json.dumps({'countries': [{
            '_id': 'rus',
            'currency': 'RUB',
            'name': 'Russia',
            "eng": "Russia",
            "lang": "ru",
        }]}))

    response = django_test.Client().post(
        '/api/set_tariff/moscow/', json.dumps(
            {
                'activation_zone': 'moscow',
                'home_zone': 'moscow',
                'categories': [{
                    'category_name': 'vip',
                    'category_type': 'application',
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'name_key': 'interval.24h',
                    'day_type': 2,
                    'currency': 'RUB',
                    'minimal': 42,
                    'paid_cancel_fix': 30,
                    'add_minimal_to_paid_cancel': False,
                }],
                'ticket': 'TAXIRATE-0001',
            }
        ),
        content_type='application/json')

    doc = yield dbh.tariffs.Doc.find_active(
        'moscow', park_id=dbh.tariffs.PARK_ID_MRT
    )
    assert doc.categories[0].paid_cancel_fix == 30
    assert not doc.categories[0].add_minimal_to_paid_cancel
    assert response.status_code == 200
    assert countries.call


@pytest.mark.filldb(tariffs='csv')
@pytest.mark.filldb(requirements='csv')
@pytest.mark.parametrize('request_body, status_code, expected', [
    ({"zones": ['linyovo']}, 200, 'linyovo.csv'),
    ({
         "zones": ['moscow']
     },
     400,
     {
         "status": "error",
         "code": "zones_not_found",
         "not_found_zones": ["moscow"]
     }),
    ({"zones": ['shebekino', 'linyovo']}, 200, 'multi.csv'),
    ({
         "zones": ['linyovo'],
         'date': '2018-01-28T14:13:29.740000Z'
     },
     400,
     {
         "status": "error",
         "code": "zones_not_found",
         "not_found_zones": ["linyovo"]
     }),
    ({
         "zones": ['linyovo'],
         'date': '2018-10-08T14:13:29.740000+03:00'
     }, 200, 'linyovo_empty_ticket.csv'),
    ({
         "zones": ['shebekino'],
         'date': '2018-10-09T10:56:29.740000+03:00'
     }, 200, 'shebekino.csv'),
    ({
         "zones": ['old_zone', 'linyovo'],
     },
     400,
     {
         "status": "error",
         "code": "old_zones",
         "old_zones": ["old_zone"]
     }),
    ({
         "zones": ['___frgt', 'linyovo'],
     },
     400,
     {
         "status": "error",
         "invalid_categories": [
             "___frgt"
         ],
         "code": "invalid_categories"
     }),
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ADMIN_AUDIT_USE_SERVICE=False)
def test_get_tariffs_list_csv(load, request_body, status_code, expected):
    response = django_test.Client().post(
        '/api/tariffs/generate_tariffs_csv/',
        json.dumps(
            request_body
        ),
        content_type='application/json'
    )
    assert response.status_code == status_code
    if response.status_code == 200:
        assert response.content.replace('\r', '') == load(expected)
    if response.status_code == 400:
        assert json.loads(response.content) == expected


@pytest.mark.skipif(
    True,
    reason='fix test TAXIBACKEND-40114'
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(requirements='csv', geoareas='csv', tariffs='csv',
                    tariff_settings='csv')
@pytest.mark.now('2018-11-21 13:00:00')
@pytest.mark.translations([
    ('geoareas', 'kirov', 'en', 'Kirov'),
    ('geoareas', 'rus', 'en', 'Rus'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.comfort', 'en', 'Comfort'),
])
@pytest.mark.config(
    LOCALES_SUPPORTED=['en'],
    ALL_CATEGORIES=[
        'express', 'econom', 'business', 'comfortplus', 'vip', 'minivan',
        'pool', 'business2', 'uberx', 'uberselect', 'uberblack', 'uberkids',
        'child_tariff'
    ],
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.parametrize('tariff_name, ts_name, home_zone, status_code, '
                         'result,log', [
    ('csv_linyovo_change.csv', None, 'linyovo', 200,
     {
         'status': 'ok',
         'tariffs': [
             {
                 'status': 'ok',
                 'name': 'tariff_my.csv'
             }
         ],
         'tariff_settings': []
     },
     'expected_csv_log_1.json'
     ),
    ('csv_kirov.csv', 'tariff_settings_kirov.csv', 'kirov', 200,
     {
         "status": "ok",
         "tariffs": [
             {
                 "status": "ok",
                 "name": "tariff_my.csv"
             }
         ],
         "tariff_settings": [
             {
                 "status": "ok",
                 "name": "tariff_settings.csv"
             }
         ]
     },
     'expected_csv_log_2.json'
     ),
    ('csv_kirov_max_price_and_multiplier.csv', None, 'kirov', 400,
        {
            'status': 'error',
            'tariffs': [
                {
                    'status': 'error',
                    'message': 'requirement_with_max_price_and_multiplier: '
                               'childchair_moscow',
                    'code': 'validation_error',
                    'name': 'tariff_my.csv'}
            ],
            'tariff_settings': [],
        },
        None,
    ),
    ('csv_linyovo_change_max_price_different_in_same_category.csv', None,
     'linyovo', 400,
        {
            'status': 'error',
            'tariffs': [
                {
                    'status': 'error',
                    'message': 'Category requirement '
                               'waiting_in_transit has different prices',
                    'code': 'validation_error',
                    'name': 'tariff_my.csv'}
            ],
            'tariff_settings': [],
        },
        None,
    ),
    ('tariffs_medic_run.csv', None,
     'kirov', 200,
        {
         "status": "ok",
         "tariffs": [
             {
                 "status": "ok",
                 "name": "tariff_my.csv"
             }
         ],
         "tariff_settings": []
        },
        'expected_waiting_price_log.json',
    ),
])
@pytest.inline_callbacks
def test_upload_tariffs_csv(patch, load, areq_request, extract_log,
                            tariff_name, ts_name, home_zone, status_code,
                            result, log):

    @areq_request
    def mocked_request(method, url, *args, **kwargs):
        if url.endswith('tariff_my.csv'):
            csv_text = load(tariff_name)
            return areq_request.response(200, csv_text)
        elif url.endswith('tariff_settings.csv'):
            if ts_name:
                csv_text = load(ts_name)
                return areq_request.response(200, csv_text)
            else:
                return areq_request.response(404)
        else:
            response = [{
                'id': '123',
                'name': 'tariff_my.csv',
                'createdAt': '2010-01-01T01:01:01+0000'
                }
            ]
            if ts_name:
                response.append({
                    'id': '321',
                    'name': 'tariff_settings.csv',
                    'createdAt': '2010-01-01T01:01:01+0000'
                })
            return areq_request.response(200, json.dumps(response))

    @patch('taxi.external.territories.get_all_countries')
    @async.inline_callbacks
    def get_all_countries(retries, retry_interval, log_extra=None):
        yield
        async.return_value([
            {'_id': 'rus', 'currency': 'RUB'}
        ])

    @patch('taxiadmin.audit.check_taxirate')
    @async.inline_callbacks
    def check_taxirate(ticket_key, login, check_author=False):
        yield async.return_value()

    @patch('taxi.internal.city_kit.currency_manager.is_known')
    @async.inline_callbacks
    def known_currency(currency, log_extra=None):
        async.return_value(True)

    @patch('taxiadmin.tariff_checks._check_translations')
    @async.inline_callbacks
    def _check_translations(tariff):
        async.return_value()

    # TODO shchesnyak: Fix test
    response = django_test.Client().post(
        '/api/tariffs/import/run/',
        json.dumps({'ticket': 'TAXIRATE-666'}),
        content_type='application/json'
    )

    assert response.status_code == status_code, response.content
    if response.status_code == 200:
        assert json.loads(response.content) == result
        log_admin = yield db.log_admin.find_one({'action': 'set_tariff'})
        log_admin.pop('_id')
        assert log_admin == extract_log(log)
    elif response.status_code == 400:
        assert json.loads(response.content) == result


@pytest.mark.asyncenv('async')
@pytest.mark.config(CATEGORY_PRICE_LIMIT_VALIDATION={
        '__default__': {
            'once': 2000,
            'waiting_price': 50,
            'minute_price': 50,
            'km_price': 60
        }
    })
@pytest.mark.config(SPECIAL_TAXIMETERS_FREE_TARIFFING_LIMIT={
    'minutes_included': 10,
    'km_included': 10,
})
@pytest.mark.parametrize('category_update, expected', [
    ({
        'minimal': 10000,
    },
    'home_zone test; category econom; type application; day type 0;'
    ' from 00:00; to 23:59; field minimal'),
    ({
         'waiting_price': 100,
     },
     'home_zone test; category econom; type application; day type 0;'
     ' from 00:00; to 23:59; field waiting_price'),
    ({
        'st': [
            {
                'p': {
                    'tpi': [{'b': 2, 'p': 100}]
                }
            }
        ],
    },
    'home_zone test; category econom; type application; day type 0;'
    ' from 00:00; to 23:59; got 100; max value 50'),
    ({
         'st': [
             {
                 'p': {
                     'dpi': [{'b': 2, 'p': 200}]
                 }
             }
         ],
     },
     'home_zone test; category econom; type application; day type 0;'
     ' from 00:00; to 23:59; got 200; max value 60'),
    ({
         'st': [
             {
                 'p': {
                     'tpi': [{'b': 50, 'p': 2}]
                 }
             }
         ],
     },
     'home_zone test; category econom; type application; day type 0;'
     ' from 00:00; to 23:59; got {\'p\': 2, \'b\': 50}; max value 10'),
    ({
         'st': [
             {
                 'p': {
                     'dpi': [{'b': 30, 'p': 3}]
                 }
             }
         ],
     },
     'home_zone test; category econom; type application; day type 0;'
     ' from 00:00; to 23:59; got {\'p\': 3, \'b\': 30}; max value 10')
])
@pytest.inline_callbacks
def test_max_price_validation(category_update, expected):
    doc = {
        'home_zone': 'test',
        'categories': [
            {
                'name': 'econom',
                'currency': 'RUB',
                'category_type': 'application',
                'req_prices': [],
                'minimal': 1,
                'to_time': '23:59',
                'name_key': 'interval.day',
                'dt': 0,
                'id': 'a6a23dff00f141d9a71d6522f4349613',
                'from_time': '00:00',
                'st': [],
                'zp': [],
            }
        ]
    }
    doc['categories'][0].update(category_update)
    doc = dbh.tariffs.Doc(doc)
    try:
        yield tariff_checks._check_max_available_price(doc)
    except tariff_checks.PriceLimitError as exc:
        assert exc.context == expected
    else:
        assert False


@pytest.mark.asyncenv('async')
@pytest.mark.config(MAX_TARIFF_PRICE_DIFFERENCE=10)
@pytest.mark.parametrize('category_update, expected', [
    ({
        'minimal': 10000,
    },
    'home_zone test; category econom; type application; day type 0;'
    ' from 00:00; to 23:59; field minimal'),
    ({
         'waiting_price': 1000,
     },
     'home_zone test; category econom; type application; day type 0;'
     ' from 00:00; to 23:59; field waiting_price'),
    ({
        'st': [
            {
                'p': {
                    'tpi': [{'b': 2, 'p': 100}]
                },
                'z': 'test'
            }
        ],
    },
    'home_zone test; category econom; type application; day type 0;'
    ' from 00:00; to 23:59; field time'),
    ({
         'st': [
             {
                 'p': {
                     'dpi': [{'b': 2, 'p': 200}]
                 },
                 'z': 'test'
             }
         ],
     },
     'home_zone test; category econom; type application; day type 0;'
     ' from 00:00; to 23:59; field distance'),
    ({
         'zp': [
             {
                 'p': {
                     'tpi': [{'b': 2, 'p': 100}]
                 },
                 'src': '123',
                 'dst': '321'
             }
         ],
     },
     'home_zone test; category econom; type application; day type 0;'
     ' from 00:00; to 23:59; field time'),
])
@pytest.inline_callbacks
def test_doc_difference_validation(category_update, expected):
    old_doc = {
        'home_zone': 'test',
        'categories': [
            {
                'name': 'econom',
                'currency': 'RUB',
                'category_type': 'application',
                'req_prices': [],
                'waiting_price': 1,
                'minimal': 1,
                'to_time': '23:59',
                'name_key': 'interval.day',
                'dt': 0,
                'id': 'a6a23dff00f141d9a71d6522f4349613',
                'from_time': '00:00',
                'st': [
                     {
                         'p': {
                             'dpi': [{'b': 2, 'p': 2}],
                             'tpi': [{'b': 2, 'p': 1}]
                         },
                         'z': 'test'
                     }
                 ],
                'zp': [
                    {
                        'p': {
                            'tpi': [{'b': 2, 'p': 1}]
                        },
                        'src': '123',
                        'dst': '321'
                    }
                ],
            }
        ]
    }
    new_doc = {
        'home_zone': 'test',
        'categories': [
            {
                'name': 'econom',
                'currency': 'RUB',
                'category_type': 'application',
                'req_prices': [],
                'minimal': 1,
                'to_time': '23:59',
                'name_key': 'interval.day',
                'dt': 0,
                'id': 'a6a23dff00f141d9a71d6522f4349613',
                'from_time': '00:00',
                'st': [],
                'zp': [],
            }
        ]
    }
    old_doc = dbh.tariffs.Doc(old_doc)
    new_doc['categories'][0].update(category_update)
    new_doc = dbh.tariffs.Doc(new_doc)
    try:
        yield tariff_checks.check_difference(old_doc, new_doc)
    except tariff_checks.PriceLimitError as exc:
        assert exc.context == expected
    else:
        assert False


@pytest.mark.asyncenv('async')
@pytest.mark.parametrize('time_array, is_ok', [
    ([('23:59', '00:00')], True),
    ([('00:00', '23:59')], True),
    ([
         ('08:00', '21:00'),
         ('21:01', '7:59')
     ], True),
    ([
         ('8:00', '21:00'),
         ('21:01', '23:59'),
         ('00:00', '07:59')
     ], True),
    ([
         ('8:00', '23:58'),
         ('23:59', '00:02'),
         ('00:03', '07:59')
     ], True),
    ([
         ('07:50', '12:45'),
     ], False),
    ([
         ('00:03', '23:58'),
     ], False),
    ([
         ('08:00', '21:00'),
         ('21:01', '00:00')
     ], False),
    ([
         ('8:00', '21:00'),
         ('21:01', '23:59'),
         ('00:00', '07:58')
     ], False),
])
def test_category_time_check(time_array, is_ok):
    category_list = []
    for time in time_array:
        category = dbh.tariffs.CategoryDocument().obj
        category.time_from = time[0]
        category.time_to = time[1]
        category_list.append(category)

    if is_ok:
        tariff_checks._validate_category_time(category_list)
    else:
        with pytest.raises(tariff_checks.OverlappingCategoriesError):
            tariff_checks._validate_category_time(category_list)


@pytest.mark.parametrize('home_zone,request_data,expected_log', [
    ('kolomna', 'set_tariff_request.json', 'expected_set_tariff_log.json'),
    ('yakutsk', 'new_tariff_request.json', 'expected_new_tariff_log.json')
])
@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.now('2018-11-21 13:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_tariff_update_log(load, patch, extract_log, home_zone,
                               request_data, expected_log):
    @patch('taxiadmin.tariff_checks._check_translations')
    @async.inline_callbacks
    def mock_check_translations(*args, **kwargs):
        yield async.return_value()

    @patch('taxiadmin.audit.check_taxirate')
    @async.inline_callbacks
    def check_taxirate(ticket_key, login, check_author=False):
        yield async.return_value()

    response = django_test.Client().post(
        '/api/set_tariff/%s/' % home_zone,
        data=load(request_data),
        content_type='application/json'

    )

    assert response.status_code == 200
    log_admin = yield db.log_admin.find_one({'action': 'set_tariff'})
    log_admin.pop('_id')
    log_admin['arguments'].pop('response')
    assert log_admin == extract_log(expected_log)


@pytest.mark.filldb(tariffs='get')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_tariff_without_requirement_intervals():
    response = django_test.Client().get(
        '/api/tariff/moscow/'
    )
    assert response.status_code == 200

    data = json.loads(response.content)
    category = data['categories'][0]
    assert 'summable_requirements' in category

    tariff_requirement = category['summable_requirements'][0]
    assert 'price' in tariff_requirement
    assert 'special_taximeters' not in tariff_requirement['price']

    doc = yield dbh.tariffs.Doc.find_active('moscow')
    tariff_requirement = doc.categories[0].summable_requirements[0]
    assert 'st' in tariff_requirement.price


@pytest.mark.parametrize('summable_requirement, is_ok', [
    ({
        'type': 'universal',
        'max_price': 100,
        'multiplier': 2,
    }, False),
    ({
        'type': 'universal',
        'max_price': 0,
        'multiplier': 2.1,
    }, True),
    ({
        'type': 'universal',
        'max_price': 100,
    }, True),
])
@pytest.inline_callbacks
def test_category_multiplier_validation(tariff, summable_requirement, is_ok):
    tariff['categories'][0]['summable_requirements'] = [summable_requirement]

    tariff_doc = dbh.tariffs.Doc._from_json(tariff)

    if is_ok:
        yield tariff_checks._check_category_requirements(
            tariff_doc.categories[0], tariff_doc.home_zone
        )
    else:
        with pytest.raises(tariff_checks.RequirementWithMultiplierAndMaxPriceError):
            yield tariff_checks._check_category_requirements(
                tariff_doc.categories[0], tariff_doc.home_zone
            )


case = helpers.case_getter(
    'request_file expected_status error_text expected_file patch_data user_login invalid_geo_node config',
    user_login='karachevda',
    invalid_geo_node=False,
    patch_data={},
    config=DEFAULT_CONFIG
)


@pytest.mark.config(
    OPERATION_CALCULATIONS_GEOSUBVENTIONS_TARIFF_PRESETS=CATEGORY_PRESET_CONFIG
)
@pytest.mark.parametrize(case.params, [
    case(
        'request/tariff_check_request_data_category_vip.json',
        200,
        None,
        'response/tariff_check_expected_response_current_empty.json',
        {
            u'change_doc_id': u'moscow:set_tariff:[global_settings,tariffs_cat-vip]',
            u'patches': {
                u'categories': {
                    u'changed': [u'vip']
                },
                u'global_settings': {
                    u'changed': [u'activation_zone', u'home_zone']
                }
            },
            u'lock_ids': [
                {u'custom': True, u'id': u'moscow:set_tariff:global_settings'},
                {u'custom': True, u'id': u'moscow:set_tariff:tariffs_cat-vip'}
            ]
        }
    ),
    case(
        'request/tariff_check_request_data_empty_caterories.json',
        200,
        None,
        'response/tariff_check_expected_response_empty_categories.json',
        {
            u'change_doc_id': u'moscow:set_tariff:[global_settings]',
            u'patches': {
                u'global_settings': {
                    u'changed': [u'activation_zone', u'home_zone']
                }
            },
            u'lock_ids': [
                {u'custom': True, u'id': u'moscow:set_tariff:global_settings'}
            ]
        }
    ),
    case(
        'request/tariff_check_request_data_category_vip_with_geo_node.json',
        200,
        None,
        'response/'
        'tariff_check_expected_response_current_empty_with_geo_node.json',
        {
            u'change_doc_id': u'moscow:set_tariff:[global_settings,tariffs_cat-vip]',
            u'patches': {
                u'categories': {
                    u'changed': [u'vip']
                },
                u'global_settings': {
                    u'changed': [u'activation_zone', u'home_zone']
                }
            },
            u'lock_ids': [
                {u'custom': True, u'id': u'moscow:set_tariff:global_settings'},
                {u'custom': True, u'id': u'moscow:set_tariff:tariffs_cat-vip'}
            ]
        }
    ),
    case(
        'request/tariff_check_request_data_category_pool.json',
        400,
        'Invalid tariffs: missing pool or drivers_pool',
        None
    ),
    case(
        'request/tariff_check_request_data_current_full.json',
        200,
        None,
        'response/tariff_check_expected_response_current_full.json',
        {
            u'change_doc_id': u'almaty:set_tariff:[global_settings,tariffs_cat-vip,tariffs_cat-pool]',
            u'patches': {
                u'categories': {
                    u'changed': [u'vip'],
                    u'removed': [u'pool']
                },
                u'global_settings': {
                    u'removed': [u'date_from']
                }
            },
            u'lock_ids': [
                {u'custom': True, u'id': u'almaty:set_tariff:global_settings'},
                {u'custom': True, u'id': u'almaty:set_tariff:tariffs_cat-vip'},
                {u'custom': True, u'id': u'almaty:set_tariff:tariffs_cat-pool'}
            ]
        },
        config={}
    ),
    case(
        request_file='request/tariff_check_request_data_current_full.json',
        expected_status=406,
        error_text='User karachevda has no access to presets {u\'pool\': None}'
    ),
    case(
        request_file='request/tariff_check_request_data_current_full.json',
        expected_status=400,
        error_text='User anyone_else has no access to'
                   ' admin/approvals/set_tariff/check/ in country kaz',
        expected_file=None,
        user_login='anyone_else',
    ),
    case(
        request_file=(
                'request/'
                'tariff_check_request_data_category_vip_with_geo_node.json'
        ),
        expected_status=400,
        error_text='invalid geo_node_name test_geo_node_name',
        expected_file=None,
        user_login='anyone_else',
        invalid_geo_node=True,
    ),
    case(
        request_file='request/tariff_check_request_data_no_geoarea.json',
        expected_status=400,
        error_text='no geoarea with name inexistent-zone',
    ),
    case(
        request_file='request/tariff_check_request_data_no_country.json',
        expected_status=400,
        error_text='no country in geoarea with name mytishchi',
    ),
    case(
        request_file='request/tariff_check_request_data_empty_meters.json',
        expected_status=400,
        error_text='Request error: [] is too short',
    ),
    case(
        request_file='request/tariff_check_request_data_invalid_meter_id.json',
        expected_status=406,
        error_text='invalid distance_price_intervals_meter_id value',
    ),
    case(
        request_file='request/tariff_check_request_data_invalid_time_id.json',
        expected_status=406,
        error_text='invalid time_price_intervals_meter_id value',
    )
])
@pytest.mark.disable_territories_api_mock
@pytest.mark.translations([
    ('tariff', 'interval.24h', 'en', 'allday'),
    ('tariff', 'currency.rub', 'en', 'ruble'),
    ('tariff', 'currency.kzt', 'en', 'tenge'),
    ('geoareas', 'moscow', 'en', 'Moscow'),
    ('geoareas', 'kolomna', 'en', 'Kolomna'),
    ('geoareas', 'almaty', 'en', 'Almaty'),
    ('tariff', 'interval.24h', 'ru', 'allday'),
    ('tariff', 'currency.rub', 'ru', 'ruble'),
    ('tariff', 'currency.kzt', 'ru', 'tenge'),
    ('geoareas', 'moscow', 'ru', 'Moscow'),
    ('geoareas', 'kolomna', 'ru', 'Kolomna'),
    ('geoareas', 'almaty', 'ru', 'Almaty'),
])
@pytest.mark.asyncenv('blocking')
def test_tariff_check(
        patch, load, areq_request, request_file, expected_status, error_text,
        expected_file, patch_data, user_login, invalid_geo_node, config
):
    uuid = 'test_uuid'
    _patch_internals(patch, config)
    request_data = json.loads(load(request_file))

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        assert ticket_body == 'tvm_ticket'
        return True

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = namedtuple('uuid4', 'hex')
        return uuid4_(uuid)

    agglomeraions_data = {'need_call': 1}

    if 'geo_node_name' in request_data and request_data.get('categories'):
        @patch('taxi.external.agglomerations.check_set_parent_for_tariff')
        @pytest.inline_callbacks
        def agglomerations_mock(tariff_zone, currency, parent_geo_node_name):
            assert tariff_zone == request_data['home_zone']
            assert currency == 'RUB'
            assert parent_geo_node_name == request_data['geo_node_name']
            agglomeraions_data['need_call'] -= 1
            if invalid_geo_node:
                raise agglomerations.AgglomerationsRequestError()
            yield
    else:
        agglomeraions_data['need_call'] -= 1

    @areq_request
    def countries(*args, **kwargs):
        assert kwargs['headers']['X-YaRequestId'] == uuid
        return areq_request.response(200, body=json.dumps({'countries': [
            {
                '_id': 'rus',
                'currency': 'RUB',
                'name': 'Russia',
                "eng": "Russia",
                "lang": "ru",
            },
            {
                '_id': 'kaz',
                'currency': 'KZT',
                'name': 'Kazakhstan',
                "eng": "Kazakhstan",
                "lang": "ka",
            },
        ]}))
    response = django_test.Client().post(
        urlresolvers.reverse(tariffs_views.set_tariff_check),
        json.dumps(request_data),
        content_type='application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN=user_login,
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == expected_status, (
        'got status %s with content=%r' % (
            response.status_code, response.content
        )
    )
    if response.status_code == 200:
        expected_data = json.loads(load(expected_file))
        if 'change_doc_id' in patch_data:
            change_doc_id = patch_data['change_doc_id']
            expected_data['change_doc_id'] = change_doc_id
        if 'lock_ids' in patch_data:
            patches = patch_data['patches']
            expected_data['data']['patches'] = patches
        if 'lock_ids' in patch_data:
            lock_ids = patch_data['lock_ids']
            expected_data['lock_ids'] = lock_ids

        assert json.loads(response.content) == expected_data
    else:
        assert error_text in json.loads(response.content)['message']
    assert agglomeraions_data == {'need_call': 0}


@pytest.mark.disable_territories_api_mock
@pytest.mark.translations([
    ('tariff', 'interval.24h', 'en', 'allday'),
    ('tariff', 'currency.rub', 'en', 'ruble'),
    ('tariff', 'service_name.hourly_rental.1_hours', 'en', 'Hourly rental'),
    ('geoareas', 'moscow', 'en', 'Moscow'),
    ('tariff', 'interval.24h', 'ru', 'allday'),
    ('tariff', 'currency.rub', 'ru', 'ruble'),
    ('tariff', 'service_name.hourly_rental.1_hours', 'ru', 'Hourly rental'),
    ('geoareas', 'moscow', 'ru', 'Moscow'),
])
@pytest.mark.parametrize(
    'additional_body', (
            {},
            {'geo_node_name': 'test'},
    )
)
@pytest.mark.now('2019-07-01T12:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_tariff_apply(patch, areq_request, additional_body):
    uuid = 'test_uuid'

    agglomeraions_data = {'need_call': 1}

    if 'geo_node_name' in additional_body:
        @patch('taxi.external.agglomerations.set_parent_for_tariff')
        @pytest.inline_callbacks
        def agglomerations_mock(tariff_zone, currency, parent_geo_node_name):
            assert tariff_zone == 'moscow'
            assert currency == 'RUB'
            assert parent_geo_node_name == additional_body['geo_node_name']
            agglomeraions_data['need_call'] -= 1
            yield
    else:
        agglomeraions_data['need_call'] -= 1

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        assert ticket_body == 'tvm_ticket'
        return True

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = namedtuple('uuid4', 'hex')
        return uuid4_(uuid)

    @patch('taxiadmin.audit.check_ticket')
    @async.inline_callbacks
    def audit_check_ticket(*args, **kwargs):
        yield async.return_value()

    @areq_request
    def countries(*args, **kwargs):
        assert kwargs['headers']['X-YaRequestId'] == uuid
        return areq_request.response(200, body=json.dumps({'countries': [{
            '_id': 'rus',
            'currency': 'RUB',
            'name': 'Russia',
            "eng": "Russia",
            "lang": "ru",
        }]}))
    body = {
        'patches': {
            'global_settings': {
                'changed': ['activation_zone', 'home_zone']
            },
            'categories': {
                'changed': ['vip']
            }
        },
        'activation_zone': 'moscow',
        'home_zone': 'moscow',
        'ticket': 'TAXIRATE-35',
        'categories': [{
            'category_name': 'vip',
            'category_type': 'application',
            'time_from': '00:00',
            'time_to': '23:59',
            'name_key': 'interval.24h',
            'day_type': 2,
            'currency': 'RUB',
            'minimal': 42,
            'paid_cancel_fix': 30,
            'add_minimal_to_paid_cancel': False,
            'summable_requirements': [
                {
                    'type': 'hourly_rental.1_hours',
                    'max_price': 1000,
                    'price': {
                        'included_distance': 100,
                        'included_time': 60,
                        'distance_multiplier': 1,
                        'time_multiplier': 1
                    },
                },
            ]
        }],
    }
    body.update(additional_body)
    response = django_test.Client().post(
        '/api/approvals/set_tariff/apply/',
        json.dumps(body),
        content_type='application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='karachevda',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {}
    doc = yield dbh.tariffs.Doc.find_one_or_not_found({'home_zone': 'moscow'})
    assert doc.pop('_id')
    assert dict(**doc) == {
        'p': '__mrt',
        'rz': ['moscow'],
        'activation_zone': 'moscow',
        'updated': datetime.datetime(2019, 7, 1, 12, 0),
        'date_from': datetime.datetime(2019, 7, 1, 12, 0),
        'home_zone': 'moscow',
        'categories': [{
            'name': 'vip',
            'category_type': 'application',
            'from_time': '00:00',
            'to_time': '23:59',
            'name_key': 'interval.24h',
            'dt': 2,
            'id': 'test_uuid',
            'currency': 'RUB',
            'minimal': 42,
            'paid_cancel_fix': 30,
            'add_minimal_to_paid_cancel': False,
            'req_prices': [
                {
                    'p': 1000,
                    't': 'hourly_rental.1_hours',
                    'price': {
                        'included_distance': 100,
                        'included_time': 60,
                        'distance_multiplier': 1,
                        'time_multiplier': 1,
                        'st': [],
                    },
                },
            ]
        }],
    }
    assert agglomeraions_data == {'need_call': 0}
