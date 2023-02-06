import pytest


@pytest.mark.config(
    EATS_SPECIAL_COMMUNICATIONS_STATS_SYNC={
        'enabled': True,
        'period': 60,
        'table_path': (
            '//home/eda-analytics-prod/'
            'product_analytics/NewYear2022/stat_by_user'
        ),
        'statistics': [
            {'name': 'favourite_retail_n', 'type': 'integer'},
            {'name': 'kg', 'type': 'integer'},
            {'name': 'kg_avg', 'type': 'double'},
            {'name': 'max_order_price', 'type': 'double'},
            {'name': 'min_order_price', 'type': 'double'},
            {'name': 'orders', 'type': 'unsigned'},
            {'name': 'orders_afternoon', 'type': 'unsigned'},
            {'name': 'orders_american', 'type': 'unsigned'},
            {'name': 'orders_avg', 'type': 'double'},
            {'name': 'orders_bk', 'type': 'unsigned'},
            {'name': 'orders_evening', 'type': 'unsigned'},
            {'name': 'orders_georgian', 'type': 'unsigned'},
            {'name': 'orders_in_office', 'type': 'unsigned'},
            {'name': 'orders_in_office_avg', 'type': 'double'},
            {'name': 'orders_italian', 'type': 'unsigned'},
            {'name': 'orders_japanese', 'type': 'unsigned'},
            {'name': 'orders_kfc', 'type': 'unsigned'},
            {'name': 'orders_md', 'type': 'unsigned'},
            {'name': 'orders_mishlen', 'type': 'unsigned'},
            {'name': 'orders_mishlen_rest_avg', 'type': 'double'},
            {'name': 'orders_morning', 'type': 'unsigned'},
            {'name': 'orders_ny', 'type': 'unsigned'},
            {'name': 'orders_ny_avg', 'type': 'double'},
            {'name': 'orders_panasia', 'type': 'unsigned'},
            {'name': 'orders_pickup', 'type': 'unsigned'},
            {'name': 'orders_pickup_avg', 'type': 'double'},
            {'name': 'orders_popcorn', 'type': 'integer'},
            {'name': 'orders_rest', 'type': 'unsigned'},
            {'name': 'orders_rest_avg', 'type': 'double'},
            {'name': 'orders_retail', 'type': 'unsigned'},
            {'name': 'orders_retail_avg', 'type': 'double'},
            {'name': 'orders_syrok', 'type': 'integer'},
            {'name': 'tips', 'type': 'double'},
            {'name': 'tips_avg', 'type': 'double'},
        ],
        'info': [
            {'name': 'first_name', 'type': 'string'},
            {'name': 'favourite_retail', 'type': 'string'},
            {'name': 'gender', 'type': 'string'},
            {'name': 'last_name', 'type': 'string'},
            {'name': 'login', 'type': 'string'},
            {'name': 'position', 'type': 'string'},
        ],
    },
)
@pytest.mark.yt(static_table_data=['yt_stats_by_user.yaml'])
async def test_sync_stats(taxi_eats_special_communications, yt_apply, pgsql):
    await taxi_eats_special_communications.run_periodic_task('sync-stats')
    cursor = pgsql['eats_special_communications'].cursor()
    cursor.execute(
        'SELECT phone_id, stats '
        'FROM eats_special_communications.user_statistics '
        'WHERE phone_id=\'phone_id\'',
    )
    stats = cursor.fetchall()

    assert stats is not None

    assert stats[0][0] == 'phone_id'
    stats[0][1]['info'] = sorted(
        stats[0][1]['info'], key=lambda info: info['name'],
    )
    stats[0][1]['statistics'] = sorted(
        stats[0][1]['statistics'], key=lambda statistics: statistics['name'],
    )

    assert stats[0][1] == {
        'info': [
            {'name': 'favourite_retail', 'value': 'Azbuka'},
            {'name': 'first_name', 'value': 'Rail'},
            {'name': 'gender', 'value': 'male'},
            {'name': 'last_name', 'value': 'Mazgutov'},
            {'name': 'login', 'value': 'mazgutov'},
            {'name': 'position', 'value': 'Team lead'},
        ],
        'statistics': [
            {'name': 'favourite_retail_n', 'value': 100.0},
            {'name': 'kg', 'value': 20.0},
            {'name': 'kg_avg', 'value': 60.0},
            {'name': 'max_order_price', 'value': 6000.0},
            {'name': 'min_order_price', 'value': 500.0},
            {'name': 'orders', 'value': 100.0},
            {'name': 'orders_afternoon', 'value': 20.0},
            {'name': 'orders_american', 'value': 15.0},
            {'name': 'orders_avg', 'value': 80.5},
            {'name': 'orders_bk', 'value': 0.0},
            {'name': 'orders_evening', 'value': 40.0},
            {'name': 'orders_georgian', 'value': 0.0},
            {'name': 'orders_in_office', 'value': 5.0},
            {'name': 'orders_in_office_avg', 'value': 2.0},
            {'name': 'orders_italian', 'value': 20.0},
            {'name': 'orders_japanese', 'value': 20.0},
            {'name': 'orders_kfc', 'value': 0.0},
            {'name': 'orders_md', 'value': 0.0},
            {'name': 'orders_mishlen', 'value': 0.0},
            {'name': 'orders_mishlen_rest_avg', 'value': 2.0},
            {'name': 'orders_morning', 'value': 40.0},
            {'name': 'orders_ny', 'value': 1.0},
            {'name': 'orders_ny_avg', 'value': 2.0},
            {'name': 'orders_panasia', 'value': 0.0},
            {'name': 'orders_pickup', 'value': 1.0},
            {'name': 'orders_pickup_avg', 'value': 2.0},
            {'name': 'orders_popcorn', 'value': 0.0},
            {'name': 'orders_rest', 'value': 90.0},
            {'name': 'orders_rest_avg', 'value': 60.0},
            {'name': 'orders_retail', 'value': 10.0},
            {'name': 'orders_retail_avg', 'value': 5.0},
            {'name': 'orders_syrok', 'value': 0.0},
            {'name': 'tips', 'value': 1000.0},
            {'name': 'tips_avg', 'value': 300.0},
        ],
    }
