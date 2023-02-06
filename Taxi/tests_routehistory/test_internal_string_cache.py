import pytest

from . import utils


@pytest.mark.xfail(reason='Known to be flaky')
async def test_internal_string_cache(routehistory_internal, pgsql):
    assert await routehistory_internal.call('StringToId', ['']) == [0]
    assert await routehistory_internal.call('IdToString', [0]) == ['']

    assert await routehistory_internal.call('StringToId', ['string1']) == [1]
    assert await routehistory_internal.call('IdToString', [1]) == ['string1']

    assert (
        await routehistory_internal.call('StringToId', ['string2'] * 500)
        == [2] * 500
    )
    assert await routehistory_internal.call('IdToString', [2]) == ['string2']

    assert await routehistory_internal.call('IdToString', [3]) == [
        'String not found',
    ]

    cursor = pgsql['routehistory'].cursor()
    utils.register_user_types(cursor)
    cursor.execute(
        'INSERT INTO routehistory.common_strings(str) VALUES '
        '(\'string3\'), (\'string4\')',
    )
    assert await routehistory_internal.call('StringToId', ['string4']) == [4]
    assert await routehistory_internal.call('IdToString', [3]) == ['string3']
    assert await routehistory_internal.call('IdToString', [4]) == ['string4']

    strs = []
    for i in range(500):
        strs.append(f'str_{i}')

    ids = await routehistory_internal.call('StringToId', strs)
    cursor.execute(
        'DELETE FROM routehistory.common_strings WHERE id = %s', [ids[0]],
    )
    assert await routehistory_internal.call(
        'IdToString', [ids[0], ids[1]],
    ) == [strs[0], strs[1]]

    cursor.execute(
        'INSERT INTO routehistory.common_strings(id, str) VALUES '
        '(9999, \'string5\')',
    )
    assert (
        await routehistory_internal.call('IdToString', [600] * 500)
        == ['String not found'] * 500
    )
    cursor.execute(
        'UPDATE routehistory.common_strings SET str = \'not string 5\' WHERE '
        'id = 9999',
    )
    assert await routehistory_internal.call('IdToString', [9999]) == [
        'string5',
    ]
