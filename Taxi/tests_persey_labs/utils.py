import pytest


def permission_variants(lab_entity_id='my_entity_lab_id', lab_id='my_lab_id'):
    return pytest.mark.parametrize(
        'headers, exp_resp_code',
        [
            ({'X-YaTaxi-Lab-Entity-Id': lab_entity_id}, 200),
            (
                {
                    'X-YaTaxi-Lab-Entity-Id': lab_entity_id,
                    'X-YaTaxi-Lab-Ids': f'{lab_id},nonexistent',
                },
                200,
            ),
            ({'X-YaTaxi-Lab-Entity-Id': 'nonexistent'}, 404),
            (
                {
                    'X-YaTaxi-Lab-Entity-Id': 'nonexistent',
                    'X-YaTaxi-Lab-Ids': lab_id,
                },
                404,
            ),
            (
                {
                    'X-YaTaxi-Lab-Entity-Id': lab_entity_id,
                    'X-YaTaxi-Lab-Ids': 'nonexistent',
                },
                404,
            ),
        ],
    )
