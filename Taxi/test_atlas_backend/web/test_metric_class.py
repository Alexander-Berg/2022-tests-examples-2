import copy

import pytest

from atlas_backend.domain import exceptions
from atlas_backend.domain import metric


DUMMY_METRIC_DICT = {
    '_id': 'requests_share_burnt',
    'database': 'atlas_orders',
    'agg_func': 'AVG',
    'en': 'Burnt Requests Share, %',
    'version': 2,
    'sql_query_raw': 'select * from atlas_orders.orders',
    'table': 'orders',
}

FIRST_METRIC_DICT = {
    '_id': 'requests_share_burnt',
    'absolute': 'requests_volume',
    'agg_func': 'AVG',
    'class_any_exists': False,
    'color': '#4651a0',
    'database': 'atlas_orders',
    'db': ['pixel', 'realtime'],
    'default': True,
    'default_leaderboard': False,
    'default_uber': None,
    'desc': '',
    'desc_en': 'Share of requests burnt',
    'divide_by': 1.0,
    'en': 'Burnt Requests Share, %',
    'formula': None,
    'id': 'requests_share_burnt',
    'ifnull': 0,
    'main_class_if_any': False,
    'map': True,
    'metric': 'Сгоревших заказов, %',
    'metrics': ['requests_share_burnt', 'requests_volume'],
    'monitoring': False,
    'optgroup': 'Заказы',
    'optgroup_en': 'Requests',
    'primary': True,
    'relative': True,
    'selection_rules': [
        'SUM(requests_share_burnt) / SUM(requests_volume)',
        'SUM(requests_volume) AS requests_volume, '
        'SUM(requests_share_burnt) AS requests_share_burnt',
        'SUM(requests_volume) AS requests_volume, '
        'SUM(requests_share_burnt) AS requests_share_burnt',
        'requests_volume, requests_share_burnt*requests_volume '
        'AS requests_share_burnt',
    ],
    'server': 'clickhouse_back_man',
    'signal': 'positive',
    'skip_primary_keys': [],
    'sql_query': None,
    'sql_query_raw': None,
    'table': 'orders',
    'target': 0.05,
    'var_geohash': None,
    'version': 2,
    'quadkey_size': 15,
    'protected_edit': False,
    'protected_view_group': None,
    'connection_type': None,
    'clique_alias': None,
    'chyt_cluster': None,
}


@pytest.mark.parametrize(
    'metric_dict, expected_metric_dict',
    [
        (
            DUMMY_METRIC_DICT,
            {
                '_id': 'requests_share_burnt',
                'absolute': None,
                'agg_func': 'AVG',
                'class_any_exists': None,
                'color': None,
                'database': 'atlas_orders',
                'db': [],
                'default': None,
                'default_leaderboard': None,
                'default_uber': None,
                'desc': None,
                'desc_en': None,
                'divide_by': None,
                'en': 'Burnt Requests Share, %',
                'formula': None,
                'id': 'requests_share_burnt',
                'ifnull': None,
                'main_class_if_any': False,
                'map': None,
                'metric': None,
                'metrics': [],
                'monitoring': None,
                'optgroup': None,
                'optgroup_en': None,
                'primary': None,
                'quadkey_size': 15,
                'relative': None,
                'selection_rules': None,
                'server': 0,
                'signal': 'positive',
                'skip_primary_keys': [],
                'sql_query': None,
                'sql_query_raw': 'select * from atlas_orders.orders',
                'table': 'orders',
                'target': None,
                'var_geohash': None,
                'version': 2,
                'protected_edit': False,
                'protected_view_group': None,
                'connection_type': None,
                'clique_alias': None,
                'chyt_cluster': None,
            },
        ),
    ],
)
async def test_metric_class_good(
        web_context, metric_dict, expected_metric_dict,
):
    result = metric.Metric.from_dict(DUMMY_METRIC_DICT).to_dict()

    assert result == expected_metric_dict


async def test_metric_class_bad(web_context):
    bad_metric_dict = {}
    # _id field is needed
    with pytest.raises(
            TypeError, match='missing 1 required positional argument: \'_id\'',
    ):
        metric.Metric.from_dict(bad_metric_dict)

    test_metric = metric.Metric.from_dict(DUMMY_METRIC_DICT)
    # id must be equal to _id
    with pytest.raises(
            exceptions.AtlasModelError,
            match='Both \'id\' and \'_id\' provided but with different values',
    ):
        test_metric.id = 'new_metric_id'


async def test_create_metric_class(web_context):
    test_metric_dict = copy.deepcopy(FIRST_METRIC_DICT)
    new_metric = metric.Metric.from_dict(test_metric_dict)
    metric_storage = metric.MetricsStorage.from_context(web_context)
    # test pymongo.errors.DuplicateKeyError
    with pytest.raises(
            exceptions.AtlasMetricStorageError,
            match='Metric was not created due to database error',
    ):
        await metric_storage.create(new_metric)

    test_metric_dict['_id'] = test_metric_dict['id'] = 'requests_share_burntt'
    test_metric_dict['quadkey_size'] = 18

    new_metric = metric.Metric.from_dict(test_metric_dict)
    await metric_storage.create(new_metric)

    metric_from_db = await web_context.mongo.atlas_metrics_list.find_one(
        {'_id': 'requests_share_burntt'},
    )

    assert metric_from_db == test_metric_dict


async def test_delete_metric_class(web_context):
    metric_storage = metric.MetricsStorage.from_context(web_context)
    await metric_storage.delete('requests_share_burntt')
    await metric_storage.delete('requests_share_burnt')

    deleted_metric_count = await web_context.mongo.atlas_metrics_list.find(
        {'_id': 'requests_share_burnt'},
    ).count()
    assert deleted_metric_count == 0


async def test_exists_metric_class(web_context):
    metric_storage = metric.MetricsStorage.from_context(web_context)

    assert await metric_storage.exists('requests_share_found')
    assert not await metric_storage.exists('requests_share_foundd')


async def test_get_metric_class(web_context):
    metric_storage = metric.MetricsStorage.from_context(web_context)
    metric_inst = await metric_storage.get('requests_share_burnt')
    metric_dict = metric_inst.to_dict()
    # change sql_query_raw key because it takes a lot of place to mock
    metric_dict['sql_query_raw'] = None

    assert metric_dict == FIRST_METRIC_DICT

    metric_inst = await metric_storage.get('requests_share_burntt')
    assert metric_inst is None


async def test_replace_metric_class(web_context):
    metric_storage = metric.MetricsStorage.from_context(web_context)

    test_metric_dict = copy.deepcopy(FIRST_METRIC_DICT)
    test_metric_dict['database'] = 'atlas_test'

    metric_to_replace = metric.Metric.from_dict(test_metric_dict)
    await metric_storage.replace(metric_to_replace)

    replaced_metric_dict = await web_context.mongo.atlas_metrics_list.find_one(
        {'_id': 'requests_share_burnt'},
    )
    assert replaced_metric_dict['database'] == 'atlas_test'

    # test that non-existing metric will not be created
    test_metric_dict['_id'] = test_metric_dict['id'] = 'requests_share_burntt'
    metric_to_replace = metric.Metric.from_dict(test_metric_dict)

    await metric_storage.replace(metric_to_replace)
    replaced_metric_dict = await web_context.mongo.atlas_metrics_list.find_one(
        {'_id': 'requests_share_burntt'},
    )
    assert replaced_metric_dict is None


@pytest.mark.parametrize('expected_metric_dict', [FIRST_METRIC_DICT])
async def test_get_list_metric_class(web_context, expected_metric_dict):
    metric_storage = metric.MetricsStorage.from_context(web_context)
    metrics = [
        item
        for item in await metric_storage.get_list()
        if item.id == 'requests_share_burnt'
    ]
    assert len(metrics) == 1
    metric_dict = metrics[0].to_dict()
    # change sql_query_raw key because it takes a lot of place to mock
    metric_dict['sql_query_raw'] = None

    assert metric_dict == expected_metric_dict
