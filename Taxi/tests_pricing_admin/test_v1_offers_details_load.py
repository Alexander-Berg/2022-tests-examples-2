import datetime as dt
from collections.abc import Iterable

import pytest


LOCAL_TIMEZONE = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo


def get_loads(pgsql, offer_id, category):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            f'SELECT * FROM ONLY cache.offers_details '
            f'WHERE offer_id=%s AND category=%s',
            (offer_id, category),
        )
        db_result = cursor.fetchall()
        fields = [column.name for column in cursor.description]
        if not db_result:
            return None
        return {field: value for field, value in zip(fields, db_result[0])}


OFFER2_YQL = (
    'PRAGMA yt.TmpFolder='
    '"//home/taxi/testsuite/tmp/pricing-admin"; '
    'PRAGMA yson.DisableStrict;$category = \'business\';'
    '$caller_link = \'caller_link_2\';$link = \'offer2\';'
    '$full_common = SELECT * FROM '
    'hahn.`home/testsuite/pricing-data-preparer-yandex-taxi-'
    'v2-prepare-common-json-log/1d/2021-09-22`WHERE caller_link '
    '= $caller_link AND (link = $link OR $link IS NULL);'
    'SELECT * FROM $full_common;$common = SELECT extra FROM '
    '$full_common;$driver_routes = $common.uuids.driver_routes['
    '$category];$user_routes = $common.uuids.user_routes[$category]'
    ';$jams = $common.uuids.route_jams;$no_jams = '
    '$common.uuids.route_no_jams;SELECT *    '
    'FROM hahn.`home/testsuite/pricing-data-preparer-yandex-taxi-'
    'v2-prepare-route-json-log/1d/2021-09-22`     '
    'WHERE caller_link = $caller_link     AND     '
    '(        (`uuid` IN (Yson::ConvertToString($driver_routes),'
    'Yson::ConvertToString($user_routes))        '
    'AND ($driver_routes IS NOT NULL OR $user_routes IS NOT NULL) '
    ')         OR (`uuid` IN (Yson::ConvertToString($jams), '
    'Yson::ConvertToString($no_jams))        '
    'AND ($jams IS NOT NULL OR $no_jams IS NOT NULL) )        '
    'OR($jams IS NULL AND $no_jams IS NULL AND $driver_routes '
    'IS NULL AND $user_routes IS NULL)    );'
    '$driver_cat = $common.uuids.driver_category[$category];'
    '$user_cat = $common.uuids.user_category[$category];'
    'SELECT *FROM hahn.`home/testsuite/pricing-data-preparer-'
    'yandex-taxi-v2-prepare-category-info-json-log/1d/2021-09-22` '
    'WHERE caller_link = $caller_link AND (    (`uuid` IN '
    '(Yson::ConvertToString($driver_cat), Yson::ConvertToString('
    '$user_cat))    AND $driver_cat IS NOT NULL AND $user_cat IS '
    'NOT NULL)    OR ($driver_cat IS NULL AND $user_cat IS NULL '
    'AND category_name=$category));$paid_supply = TRUE;SELECT '
    '*FROM hahn.`home/testsuite/pricing-data-preparer-yandex-taxi'
    '-v2-calc-paid-supply-category-json-log/1d/2021-09-22` '
    'WHERE $paid_supply AND caller_link = $caller_link   '
    'AND category_name=$category;'
)


@pytest.mark.parametrize(
    'offer_id, category, response_code, second_code',
    [
        ('offerX', 'econom', 404, 404),
        ('offer1', 'business', 200, 200),
        ('offer2', 'business', 200, 208),
    ],
    ids=['absent', 'dynamic', 'static'],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['yql_loads.sql'])
@pytest.mark.yt(
    schemas=[
        'yt_v2_prepare_common_schema.yaml',
        'yt_v2_prepare_route_schema.yaml',
        'yt_v2_prepare_category_info_schema.yaml',
        'yt_backend_variables_schema.yaml',
    ],
    dyn_table_data=[
        'yt_v2_prepare_common.yaml',
        'yt_v2_prepare_route.yaml',
        'yt_v2_prepare_category_info.yaml',
        'yt_backend_variables.yaml',
    ],
)
@pytest.mark.now('2020-09-23 12:00:00.0000+03')
async def test_v1_offers_details_load(
        taxi_pricing_admin,
        pgsql,
        offer_id,
        category,
        response_code,
        mockserver,
        testpoint,
        second_code,
        yt_apply_force,
        load_json,
):
    @mockserver.json_handler('/yql/api/v2/operations')
    def _mock_yql_run(request):
        assert offer_id == 'offer2'
        data = request.json
        assert data['content'].replace('\n', '') == OFFER2_YQL
        return {'id': 'link_' + offer_id}

    @mockserver.json_handler('/yql/api/v2/operations/link_offer2/share_id')
    def _mock_user1_share_id(request):
        return 'share_user1'

    @testpoint('loading_static_started')
    async def loading_static_started(data):
        pass

    @testpoint('loading_dynamic_started')
    async def loading_dynamic_started(data):
        pass

    response = await taxi_pricing_admin.post(
        'v1/offers/details/load',
        params={'offer_id': offer_id, 'category': category},
    )
    assert response.status_code == response_code

    if offer_id == 'offer1':
        await loading_dynamic_started.wait_call()
    elif offer_id == 'offer2':
        await loading_static_started.wait_call()

    def set_local_timezone(value):
        return (
            dt.datetime.fromisoformat(value)
            .astimezone(LOCAL_TIMEZONE)
            .isoformat()
        )

    base = load_json(offer_id + '.json')
    loads = get_loads(pgsql, offer_id, category)
    if loads:
        loads.pop('last_access_time')

    if isinstance(base, Iterable):
        for item in base:
            if isinstance(base[item], Iterable) and 'timestamp' in base[item]:
                base[item]['timestamp'] = set_local_timezone(
                    base[item]['timestamp'],
                )
    assert loads == base

    response = await taxi_pricing_admin.post(
        'v1/offers/details/load',
        params={'offer_id': offer_id, 'category': category},
    )
    assert response.status_code == second_code
