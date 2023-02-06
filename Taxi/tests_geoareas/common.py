import datetime

import pytest
import pytz

DEFAULT_LOCALE = 'ru'

GEOAREAS_KEYSET = {
    'msk': {'ru': 'Москва', 'en': 'Moscow'},
    'spb': {'ru': 'Питер', 'en': 'SPB'},
    'removed': {'ru': 'Удалено', 'en': 'Removed'},
    'removed_in_future': {
        'ru': 'Удалено в будущем',
        'en': 'Removed in future',
    },
}

SUBVENTION_GEOAREA_HEADER = {'X-YaTaxi-Draft-Id': 'some_id'}


def deep_approx(obj, **kwargs):
    if isinstance(obj, dict):
        return {key: deep_approx(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [deep_approx(value) for value in obj]
    if isinstance(obj, float):
        return pytest.approx(obj, **kwargs)
    return obj


async def make_edit_or_check_request(
        taxi_geoareas, collection_endpoint, req_body, is_check_handle, header,
):
    if not is_check_handle:
        res = await taxi_geoareas.put(
            collection_endpoint, req_body, headers=header,
        )
    else:
        res = await taxi_geoareas.post(
            collection_endpoint, req_body, headers=header,
        )
    return res


def fill_correct_translations(geoareas, locale):
    if locale is None:
        locale = DEFAULT_LOCALE
    for area in geoareas:
        area['translation'] = GEOAREAS_KEYSET[area['name']][locale]


def strip_translations(geoareas):
    for area in geoareas:
        if 'translation' in area:
            del area['translation']


def create_name_object(area):
    name_object = {}
    name_object['name'] = area['name']
    if 'translation' in area:
        name_object['translation'] = area['translation']
    return name_object


def datetime_string_to_datetime(datetime_string):
    correct_iso = datetime_string[:-2] + ':' + datetime_string[-2:]
    return datetime.datetime.fromisoformat(correct_iso)


def geoareas_correct_datetimes(geoareas):
    for area in geoareas:
        if 'created' in area:
            area['created'] = datetime_string_to_datetime(area['created'])
        if 'removed_at' in area:
            area['removed_at'] = datetime_string_to_datetime(
                area['removed_at'],
            )


def expected_add_timezone_info(expected):
    for area in expected:
        if 'created' in area:
            area['created'] = area['created'].replace(tzinfo=pytz.UTC)
        if 'removed_at' in area:
            area['removed_at'] = area['removed_at'].replace(tzinfo=pytz.UTC)


def check_get_response(res, expected, locale, many=False, only_names=False):
    got = res.json()

    if only_names:
        expected = list(map(create_name_object, expected))
        assert 'geoareas_names' in got
        geoareas = got['geoareas_names']
    else:
        assert 'geoareas' in got
        geoareas = got['geoareas']

    assert isinstance(geoareas, list)
    if geoareas or many:
        assert res.status_code == 200
    else:
        assert res.status_code == 404

    if locale == 'ignore':
        strip_translations(geoareas)
    else:
        fill_correct_translations(expected, locale)

    geoareas_correct_datetimes(geoareas)
    expected_add_timezone_info(expected)

    geoareas.sort(key=lambda x: (x.get('geoarea_type', ''), x['name']))
    expected.sort(key=lambda x: (x.get('geoarea_type', ''), x['name']))

    assert geoareas == deep_approx(expected)
