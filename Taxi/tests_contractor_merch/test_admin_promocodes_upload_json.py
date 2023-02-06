import copy
import typing

import pytest

ENDPOINT = '/admin/contractor-merch/v1/promocodes/upload-json'

DEFAULT_PROMOCODES = ['QAZWSX', 'S7DS9S']
ADDITIONAL_PROMOCODES = [
    'QWERTY',
    'S59SJ2 ',
    '  92KNDI',
    '   KDJ489   ',
    'DL34J9   ',
]
STRIP_SYMBOLS = '\r\n\t '
DEFAULT_PROMOCODE_LENGTH = len(ADDITIONAL_PROMOCODES[0].strip(STRIP_SYMBOLS))


DEFAULT_PARAMS: typing.Dict[str, typing.Any] = {
    'feeds_admin_id': 'admin_1',
    'expect_same_promocode_length': False,
    'promocodes': ADDITIONAL_PROMOCODES,
}


def _trimmed(lines: typing.Iterable[str]) -> typing.List[str]:
    return [line.strip(STRIP_SYMBOLS) for line in lines]


def _validate_existing_promocodes(
        pgsql, expected_promocodes: typing.Optional[typing.List[str]] = None,
):
    expected_promocodes = expected_promocodes or DEFAULT_PROMOCODES
    cursor = pgsql['contractor_merch'].cursor()
    cursor.execute(
        """
            SELECT
                number
            FROM contractor_merch.promocodes
        """,
    )
    result = sorted(_trimmed(row[0] for row in cursor.fetchall()))
    assert result == sorted(_trimmed(expected_promocodes))


@pytest.mark.pgsql('contractor_merch', files=['init_promocodes.sql'])
async def test_ok(taxi_contractor_merch, pgsql):
    _validate_existing_promocodes(pgsql)
    response = await taxi_contractor_merch.post(ENDPOINT, json=DEFAULT_PARAMS)
    assert response.status_code == 200
    assert response.json() == {'inserted_count': 5}
    expected_promocodes = DEFAULT_PROMOCODES + ADDITIONAL_PROMOCODES
    _validate_existing_promocodes(pgsql, expected_promocodes)


async def test_empty_array_provided(taxi_contractor_merch):
    params = copy.deepcopy(DEFAULT_PARAMS)
    params['promocodes'] = []
    response = await taxi_contractor_merch.post(ENDPOINT, json=params)
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'No promocodes provided',
    }


@pytest.mark.pgsql('contractor_merch', files=['init_promocodes.sql'])
@pytest.mark.parametrize('expect_same_promocode_length', [True, False])
async def test_expect_same_promocode_length(
        taxi_contractor_merch, pgsql, expect_same_promocode_length,
):
    promocodes = ADDITIONAL_PROMOCODES + [
        'Another_promocode',
        'Too_long_promocode',
    ]
    params = copy.deepcopy(DEFAULT_PARAMS)
    params['expect_same_promocode_length'] = expect_same_promocode_length
    params['promocodes'] = promocodes
    response = await taxi_contractor_merch.post(ENDPOINT, json=params)
    if expect_same_promocode_length:
        assert response.status_code == 400
        assert response.json() == {
            'code': '400',
            'message': (
                f'Expected promocode length={DEFAULT_PROMOCODE_LENGTH}. '
                f'Invalid indexes: {len(ADDITIONAL_PROMOCODES) + 1}, '
                f'{len(ADDITIONAL_PROMOCODES) + 2}'
            ),
        }
    else:
        assert response.status_code == 200
        assert response.json() == {
            'inserted_count': len(ADDITIONAL_PROMOCODES) + 2,
        }
        expected_promocodes = list(set(DEFAULT_PROMOCODES + promocodes))
        _validate_existing_promocodes(pgsql, expected_promocodes)


async def test_invalid_promocode_not_printable(taxi_contractor_merch):
    invalid_promocode = '\xFFqwert'
    assert len(invalid_promocode) == DEFAULT_PROMOCODE_LENGTH
    params = copy.deepcopy(DEFAULT_PARAMS)
    params['promocodes'].append(invalid_promocode)
    response = await taxi_contractor_merch.post(ENDPOINT, json=params)
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Expected all promocodes to be printable. '
            f'Invalid indexes: {len(ADDITIONAL_PROMOCODES) + 1}'
        ),
    }


async def test_duplicate_promocodes_in_input(taxi_contractor_merch):
    params = copy.deepcopy(DEFAULT_PARAMS)
    params['promocodes'].extend(ADDITIONAL_PROMOCODES[:2])
    response = await taxi_contractor_merch.post(ENDPOINT, json=params)
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Found duplicates. Invalid indexes: 6, 7',
    }


@pytest.mark.pgsql('contractor_merch', files=['init_promocodes.sql'])
async def test_existing_promocodes_intersection(taxi_contractor_merch, pgsql):
    _validate_existing_promocodes(pgsql)
    new_promocodes = (
        [DEFAULT_PROMOCODES[1]]
        + ADDITIONAL_PROMOCODES
        + [DEFAULT_PROMOCODES[0]]
    )
    params = copy.deepcopy(DEFAULT_PARAMS)
    params['promocodes'] = new_promocodes
    response = await taxi_contractor_merch.post(ENDPOINT, json=params)

    assert response.status_code == 400
    _validate_existing_promocodes(pgsql)
    assert response.json() == {
        'code': '400',
        'message': 'Found existing promocodes. Invalid indexes: 1, 7',
    }
