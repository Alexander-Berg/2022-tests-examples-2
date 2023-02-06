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
        'timetable',
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
        'oebs_depot_id',
    ]

    result = do_select_from(cursor, now, keys, 'depots_wms.depots')
    return sorted(result, key=lambda k: k['depot_id'])


def get_zones_wms(cursor, now):
    keys = [
        'zone_id',
        'depot_id',
        'status',
        'created',
        'updated',
        'delivery_type',
        'timetable',
        'zone',
        'effective_from',
        'effective_till',
    ]
    result = do_select_from(cursor, now, keys, 'depots_wms.zones')
    return sorted(result, key=lambda k: k['zone_id'])


@pytest.mark.experiments3(
    name='grocery_depots_default_depot_phone_number',
    consumers=['grocery-depots/depot-phone-number'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'phone_number': '8(000)9999999'},
    is_config=True,
)
@pytest.mark.suspend_periodic_tasks('wms-depots-sync-periodic')
async def test_depots_wms_import(
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
    expected_depots = []
    for expected_depot in load_json('depots_wms_from_db.json')['answer']:
        if 'phone_number' not in expected_depot:
            expected_depot['phone_number'] = '8(000)9999999'
        expected_depots.append(expected_depot)
    expected_depots.sort(key=lambda x: x['depot_id'])
    result.sort(key=lambda x: x['depot_id'])
    assert len(result) == len(expected_depots)
    assert result == expected_depots

    assert mock_wms_response.times_called == 2


@pytest.mark.experiments3(
    name='grocery_depots_default_depot_phone_number',
    consumers=['grocery-depots/depot-phone-number'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'phone_number': '8(000)9999999'},
    is_config=True,
)
@pytest.mark.suspend_periodic_tasks('wms-depots-sync-periodic')
async def test_depots_wms_import_closed_depot(
        taxi_grocery_depots, mockserver, pgsql, load_json,
):
    now = datetime.datetime.now()

    @mockserver.json_handler('/grocery-wms/api/external/stores/v1/list')
    def mock_wms_response(request):
        if request.json['cursor'] == '':
            return load_json('wms_response_closed.json')
        return {}

    await taxi_grocery_depots.run_periodic_task('wms-depots-sync-periodic')

    db = pgsql['grocery_depots']
    cursor = db.cursor()
    result = get_depots_wms(cursor, now)
    result.sort(key=lambda x: x['depot_id'])

    expected_depots = []
    for expected_depot in load_json('depots_wms_from_db_closed.json')[
            'answer'
    ]:
        if 'phone_number' not in expected_depot:
            expected_depot['phone_number'] = '8(000)9999999'
        expected_depots.append(expected_depot)
    expected_depots.sort(key=lambda x: x['depot_id'])

    assert result == expected_depots
    assert mock_wms_response.times_called == 2


@pytest.mark.pgsql('grocery_depots', files=['depots_wms.sql'])
@pytest.mark.suspend_periodic_tasks('wms-zones-sync-periodic')
async def test_wms_zones_sync(
        taxi_grocery_depots, mockserver, pgsql, load_json,
):
    """
    Test zones received from WMS handles are stored in DB
    """
    now = datetime.datetime.now()

    @mockserver.json_handler('/grocery-wms/api/external/zones/v1/list')
    def mock_wms_zones_response(request):
        cursor = request.json['cursor']
        if cursor == '':
            return load_json('wms_zones_response.json')
        return load_json(f'wms_zones_response_{cursor}.json')

    db = pgsql['grocery_depots']
    cursor = db.cursor()

    result = get_zones_wms(cursor, now)
    assert not result

    await taxi_grocery_depots.run_periodic_task('wms-zones-sync-periodic')

    assert mock_wms_zones_response.times_called == 2
    result = get_zones_wms(cursor, now)
    assert len(result) == 6


@pytest.mark.pgsql('grocery_depots', files=['depots_wms.sql'])
async def test_point_equality(pgsql):
    """
    Test which is testing the following error:
    could not identify an equality operator for type point
    """
    db = pgsql['grocery_depots']
    cursor = db.cursor()
    # in bad case there will be programming error
    cursor.execute(
        'UPDATE depots_wms.depots'
        '   SET location=(1,1)::depots_wms.depot_location'
        '   WHERE depot_id'
        '   = \'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000\'',
    )
