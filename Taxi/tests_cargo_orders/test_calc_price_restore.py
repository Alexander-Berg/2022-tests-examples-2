import pytest

_PROVIDER_ORDER_ID = '87d884e54e3f14ccbe97dfc9e1e864c3'
_ORDER_ID = 'b1fe01dd-c302-4727-9f80-6e6c5e210a9f'
_TABLES_TO_RESTORE = ['cargo_orders.orders', 'cargo_orders.orders_performers']


@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.parametrize(
    'yt_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                CARGO_ORDERS_ENABLE_YT=True,
                CARGO_ORDERS_ENABLE_YT_RESTORE=True,
            ),
        ),
        False,
    ],
)
async def test_calc_price_restore(
        taxi_cargo_orders, yt_apply, pgsql, yt_enabled,
):
    async def _restore():
        _check_pg_order(
            pgsql, _TABLES_TO_RESTORE, _ORDER_ID, expected_in_db=False,
        )
        response = await taxi_cargo_orders.post(
            '/v1/calc-price',
            json={
                'user_id': 'mock-user',
                'order_id': _PROVIDER_ORDER_ID,
                'cargo_ref_id': 'mock-claim',
                'tariff_class': 'mock-tariff',
                'status': 'finished',
                'taxi_status': 'complete',
                'driver_id': 'mock-driver',
                'source_type': 'presetcar',
            },
        )
        assert response.status == 200
        assert response.json() == {'is_cargo_pricing': False}
        _check_pg_order(
            pgsql, _TABLES_TO_RESTORE, _ORDER_ID, expected_in_db=yt_enabled,
        )
        if yt_enabled:
            _check_restored_all_columns(pgsql, _TABLES_TO_RESTORE, _ORDER_ID)

    await _restore()
    _drop_records(pgsql, _TABLES_TO_RESTORE, _ORDER_ID)
    await _restore()


def _check_pg_order(pgsql, tables, order_id, *, expected_in_db: bool):
    for table in tables:
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            f"""
            SELECT
             order_id
            FROM {table} WHERE order_id::uuid = %s
            """,
            (order_id,),
        )
        row = cursor.fetchone()
        assert (row is not None) == expected_in_db


def _check_restored_all_columns(pgsql, tables, order_id):
    for table in tables:
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            f"""
            SELECT
             *
            FROM {table} WHERE order_id::uuid = %s
            """,
            (order_id,),
        )
        fields = [column.name for column in cursor.description]
        row = dict(zip(fields, cursor.fetchone()))
        not_restored = []
        for key, value in row.items():
            if value is None:
                not_restored.append(key)
        if not_restored:
            sql = (
                'restore_order.sql'
                if table == 'cargo_orders.orders'
                else 'restore_order_performer.sql'
            )
            assert False, (
                f'Table: {table}, columns: {", ".join(not_restored)} '
                f'are not restored. Please, add these columns to: '
                f'cargo-orders/src/utils/restore_from_yt.cpp, '
                f'cargo-orders/src/sql/{sql}, '
                f'cargo-orders/testsuite/tests_cargo_orders/'
                f'static/test_calc_price_restore/yt_raw_denorm.yaml'
            )


def _drop_records(pgsql, tables, order_id):
    for table in tables:
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            f"""DELETE FROM {table} WHERE order_id::uuid = %s""", (order_id,),
        )
