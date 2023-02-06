import decimal

import pytest


@pytest.mark.pgsql('overlord_catalog', files=[])
@pytest.mark.suspend_periodic_tasks('wms-stocks-sync-periodic')
async def test_basic(taxi_overlord_catalog, pgsql, mockserver, load_json):
    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def mock_wms(request):
        if request.json['cursor']:
            return load_json('wms_stock_response_end.json')
        return load_json('wms_stock_response_1.json')

    await taxi_overlord_catalog.run_periodic_task('wms-stocks-sync-periodic')
    assert mock_wms.times_called == 2

    db = pgsql['overlord_catalog']
    cursor = db.cursor()
    cursor.execute(
        'SELECT depot_id, product_id, in_stock '
        'from catalog_wms.stocks order by 1, 2',
    )
    result = cursor.fetchall()
    assert result == [
        (
            'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
            '115959d1fe98402ca80f284e26fae9b5000200010000',
            decimal.Decimal('32.0000'),
        ),
        (
            'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
            '1454985539be431da4653299797829ec000200010000',
            decimal.Decimal('27.0000'),
        ),
        (
            'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
            '736a003a0fec47faaeef64128ec6bd55000200010000',
            decimal.Decimal('30.0000'),
        ),
        (
            'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
            'a26152b2d33b4a3f8176e3d96940ce9a000100010001',
            decimal.Decimal('10.0000'),
        ),
        (
            'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
            'd48162fdc49e4820b6fddc1b6bcdd46f000200010000',
            decimal.Decimal('21.0000'),
        ),
        (
            'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
            'fb70ba514e8e48378242939903da92f0000300010000',
            decimal.Decimal('34.0000'),
        ),
    ]
