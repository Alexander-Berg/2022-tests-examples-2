import pytest


def get_data_base(pgsql):
    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """
    SELECT id, place_id, status, cashback, starts, ends, updated_at
    FROM eats_restapp_promo.place_plus_activation
    ORDER BY id
    """,
    )
    return list(cursor)


def make_request(place_id, cashback, add_ends=False):
    result = {
        'place_id': place_id,
        'cashback': cashback,
        'starts': '2019-12-11T12:00:00+0300',
        'updated_at': '2019-12-11T12:00:10+0300',
    }
    if add_ends:
        result['ends'] = '2019-12-11T12:00:00+0300'
    return result


def format_result(data):
    result = []
    for part_to_format in data:
        part = [
            part_to_format[0],
            part_to_format[1],
            part_to_format[2],
            part_to_format[3],
            part_to_format[4].strftime('%Y-%m-%dT%H:%M:%S'),
        ]
        if part_to_format[5] is None:
            part.append(None)
        else:
            part.append(part_to_format[5].strftime('%Y-%m-%dT%H:%M:%S'))
        result.append(part)

    return result


def expected_line_in_table(id_in_table, place_id, cashback, add_ends=False):
    ends = None
    if add_ends:
        ends = '2019-12-11T12:00:00'
    return [
        id_in_table,
        place_id,
        'active',
        cashback,
        '2019-12-11T12:00:00',
        ends,
    ]


@pytest.mark.now('2021-08-12T17:38:00.00')
@pytest.mark.parametrize(
    'cashbacks, in_table',
    [
        (
            [make_request('87263', '10')],
            [expected_line_in_table(1, '87263', 10)],
        ),
        (
            [make_request('87263', '15', True)],
            [expected_line_in_table(1, '87263', 15, True)],
        ),
        (
            [make_request('87263', '123')],
            [expected_line_in_table(1, '87263', 123)],
        ),
        (
            [make_request('87263', '10')],
            [expected_line_in_table(1, '87263', 10)],
        ),
        (
            [make_request('1234', '1234', True)],
            [
                expected_line_in_table(1, '87263', 10),
                expected_line_in_table(2, '1234', 1234, True),
            ],
        ),
        (
            [
                make_request('1', '1', True),
                make_request('2', '2'),
                make_request('3', '3', True),
                make_request('4', '4'),
            ],
            [
                expected_line_in_table(1, '87263', 10),
                expected_line_in_table(2, '1', 1, True),
                expected_line_in_table(3, '2', 2),
                expected_line_in_table(4, '3', 3, True),
                expected_line_in_table(5, '4', 4),
            ],
        ),
        (
            [
                make_request('1', '1', True),
                make_request('2', '2'),
                make_request('3', '3', True),
                make_request('4', '4'),
                make_request('87263', '15', True),
            ],
            [
                expected_line_in_table(1, '87263', 15, True),
                expected_line_in_table(2, '1', 1, True),
                expected_line_in_table(3, '2', 2),
                expected_line_in_table(4, '3', 3, True),
                expected_line_in_table(5, '4', 4),
            ],
        ),
    ],
)
async def test_transfer_data_one_line_without_ends(
        taxi_eats_restapp_promo, pgsql, cashbacks, in_table,
):
    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/plus/cashback/transfer',
        json={'cashbacks': cashbacks},
    )

    assert response.status_code == 200

    db = get_data_base(pgsql)

    assert len(format_result(db)) == len(in_table)
    assert format_result(db) == in_table
