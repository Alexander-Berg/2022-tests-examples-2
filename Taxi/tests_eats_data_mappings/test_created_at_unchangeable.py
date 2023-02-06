from psycopg2.errors import RaiseException
import pytest


async def test_created_at_unchangeable(pgsql):
    cursor = pgsql['eats_data_mappings'].cursor()

    request = (
        'INSERT INTO eats_data_mappings.entity_pairs '
        'VALUES (1, \'t1\', \'v1\', '
        '\'t2\', \'v2\', \'2022-05-03 10:00:00+03\', NULL, '
        '\'2022-05-01 10:00:00+03\');'
    )
    cursor.execute(request)

    request = (
        'UPDATE eats_data_mappings.entity_pairs '
        'SET created_at=\'2022-03-20 10:00:00+03\' WHERE primary_entity_type = \'t1\';'
    )
    try:
        cursor.execute(request)
    except RaiseException:
        pass
    except Exception:
        raise
    else:
        assert False, (
            'Execution of created_at field update '
            'did not fail but it should have'
        )
