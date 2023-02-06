# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint:disable= unused-variable, redefined-builtin, invalid-name
# pylint:disable= global-statement, no-else-return
import pytest

from . import conftest

calls_count = 0


# @pytest.fixture()
def db_rows_get(pgsql, table=''):
    cursor = pgsql['surge'].cursor()
    cursor.execute('SELECT * FROM {};'.format(table))
    return cursor.fetchall()
    # def _db_rows_get(table):
    #     cursor = pgsql['surge'].cursor()
    #     cursor.execute('SELECT * FROM {}};'.format(table))
    #     return cursor.fetchall()
    #
    # return _db_rows_get


@pytest.fixture(name='surger_handlers')
def _mock_surger_handlers(mockserver):
    @mockserver.json_handler('/eda-surge-calculator/v1/calc-surge')
    def _mock_surge_calculator(request):
        global calls_count

        calls_count += 1

        return {
            'results': [
                {
                    'calculator_name': 'eats_surge_calculator',
                    'results': [
                        {
                            'place_id': 1,
                            'result': {
                                'total': 30,
                                'busy': 10,
                                'free': 20,
                                'load_level': 15,
                                'surge_level': 0,
                                'delivery_fee': 0,
                                'extra': {
                                    'conditionally_busy': 0,
                                    'conditionally_free': 0,
                                },
                            },
                        },
                        {
                            'place_id': 2,
                            'result': {
                                'total': 30,
                                'busy': 10,
                                'free': 20,
                                'load_level': 15,
                                'surge_level': 0,
                                'delivery_fee': 0,
                            },
                        },
                        {
                            'place_id': 3,
                            'result': {
                                'total': 30,
                                'busy': 10,
                                'free': 20,
                                'load_level': 15,
                                'surge_level': 0,
                                'delivery_fee': 0,
                            },
                        },
                        {
                            'place_id': 4,
                            'result': {
                                'total': 30,
                                'busy': 10,
                                'free': 20,
                                'load_level': 15,
                                'surge_level': 0,
                                'delivery_fee': 0,
                            },
                        },
                        {
                            'place_id': 5,
                            'result': {
                                'total': 30,
                                'busy': 10,
                                'free': 20,
                                'load_level': 15,
                                'surge_level': 0,
                                'delivery_fee': 0,
                            },
                        },
                    ],
                },
            ],
            'errors': [],
        }


@pytest.mark.eats_catalog_storage_cache(conftest.PLACES)
@pytest.mark.now('2021-05-11T03:00:30+00:00')
@pytest.mark.parametrize(
    'table,count',
    (
        pytest.param('taxi_surger_parts_00', 0, id='empty_table_before'),
        pytest.param('taxi_surger_parts_04', 0, id='empty_table_after'),
        pytest.param('taxi_surger_parts_02', 5, id='filled_table'),
    ),
)
async def test_surger(
        taxi_eats_surge_planner, surger_handlers, pgsql, table, count,
):
    await taxi_eats_surge_planner.run_distlock_task('surge-worker')
    assert calls_count > 0
    assert len(db_rows_get(pgsql, table)) == count
