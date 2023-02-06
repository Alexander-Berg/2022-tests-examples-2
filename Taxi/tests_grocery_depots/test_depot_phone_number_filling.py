import datetime

import pytest
import pytz


def do_select_from(cursor, now, keys, table):
    select_keys = ', '.join(keys)
    cursor.execute(f'SELECT {select_keys} FROM {table}')
    result = []
    for item in cursor.fetchall():
        push = {}
        for i, value in enumerate(item):
            push[keys[i]] = value
        updated = push['updated'].astimezone(pytz.UTC).replace(tzinfo=None)
        updated = (updated - now) < datetime.timedelta(seconds=5)
        push['updated'] = updated
        if ('open_ts' in push) and (push['open_ts'] is not None):
            push['open_ts'] = str(
                push['open_ts'].astimezone(pytz.UTC).replace(tzinfo=None),
            )
        result.append(push)
    return result


def get_depots_wms(cursor, now):
    keys = [
        'depot_id',
        'external_id',
        'status',
        'cluster',
        'title',
        'name',
        'region_id',
        'address',
        'location',
        'currency',
        'timezone',
        'source',
        'root_category_id',
        'assortment_id',
        'price_list_id',
        'updated',
        'company_id',
        'allow_parcels',
        'options',
        'phone_number',
        'email',
        'directions',
        'telegram',
        'open_ts',
    ]
    result = do_select_from(cursor, now, keys, 'depots_wms.depots')
    return sorted(result, key=lambda k: k['depot_id'])


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.suspend_periodic_tasks('wms-depots-sync-periodic')
async def test_depot_phone_number_filling(
        taxi_grocery_depots, mockserver, pgsql, load_json,
):
    now = datetime.datetime.now()

    @mockserver.json_handler('/grocery-wms/api/external/stores/v1/list')
    def mock_wms_response(request):
        if request.json['cursor'] == '':
            return load_json('wms_response.json')
        if request.json['cursor'] == 'last-cursor':
            return load_json('wms_response_last.json')
        return {}

    await taxi_grocery_depots.run_periodic_task('wms-depots-sync-periodic')
    db = pgsql['grocery_depots']
    cursor = db.cursor()
    result = get_depots_wms(cursor, now)

    expected_depots = load_json('expected_depots.json')

    result.sort(key=lambda x: x['depot_id'])
    expected_depots.sort(key=lambda x: x['depot_id'])

    assert len(result) == len(expected_depots)
    assert result == expected_depots
    assert mock_wms_response.times_called == 2
