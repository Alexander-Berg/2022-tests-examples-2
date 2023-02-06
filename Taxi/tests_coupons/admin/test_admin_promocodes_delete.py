import pytest

from tests_coupons import util


DATE_FORMAT = '%Y-%m-%dT%H:%M'


HEADERS = {
    'X-Yandex-Uid': '75170007',
    'User-Agent': 'Opera/9.99 (Windows NT 0.0; EN)',
}


@pytest.mark.now('2016-12-01T12:00:00.0')
@pytest.mark.parametrize('headers', [None, HEADERS])  # headers are optional
@pytest.mark.filldb(promocode_usages='used')  # usages for 'firstlimit' series
@pytest.mark.parametrize('collections_tag', util.PROMOCODES_DB_MODE_PARAMS)
@pytest.mark.parametrize(
    'series_id, full_delete, expected_code',
    [
        *[
            pytest.param('notexist', full_delete, 404, id='series not found')
            for full_delete in (True, False, None)
        ],
        pytest.param('firstlimit', True, 400, id='can not delete used series'),
        pytest.param('firstlimit', False, 200, id='can stop used series'),
        *[
            pytest.param('basic', full_delete, 200, id='ok delete/stop')
            for full_delete in (True, False, None)
        ],
    ],
)
async def test_admin_promocodes_delete(
        taxi_coupons,
        mongodb,
        headers,
        series_id,
        full_delete,
        expected_code,
        collections_tag,
):
    promocodes = util.tag_to_promocodes_for_read(mongodb, collections_tag)

    data = {'series_id': series_id}
    if full_delete is not None:
        data['full_delete'] = full_delete

    response = await taxi_coupons.post(
        '/admin/promocodes/delete/', json=data, headers=headers,
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        response_json = response.json()
        assert response_json['series'] == series_id
        assert response_json['action'] == 'del'

        series = mongodb.promocode_series.find_one({'_id': series_id})

        if full_delete:
            assert not list(promocodes.find({'series_id': series_id}))
            assert not series

        else:
            response_set_update = response_json['update']['$set']
            assert (
                series['requires_activation_after'].strftime(DATE_FORMAT)
                == response_set_update['requires_activation_after'][:16]
                == '2016-12-01T12:00'
            )
