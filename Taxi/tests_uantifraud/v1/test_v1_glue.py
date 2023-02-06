import pytest

_REQUEST = {
    'sources': ['taxi', 'eats', 'grocery'],
    'passport_uid': '123456789',
}


@pytest.mark.parametrize(
    'sources',
    [
        [],
        ['taxi'],
        ['eats'],
        ['grocery'],
        ['taxi', 'eats'],
        ['taxi', 'grocery'],
        ['eats', 'grocery'],
    ],
)
async def test_base(taxi_uantifraud, sources):
    resp = await taxi_uantifraud.post(
        '/v1/glue', json={**_REQUEST, **{'sources': sources}},
    )
    if not sources:
        assert resp.status_code == 400
        return
    assert resp.status_code == 200
    assert resp.json() == {
        'sources': {source: {'passport_uids': []} for source in sources},
    }


async def test_find_exists_glue(taxi_uantifraud):
    resp = await taxi_uantifraud.post(
        '/v1/glue', json={**_REQUEST, **{'passport_uid': '1525829053'}},
    )
    assert resp.status_code == 200
    assert resp.json() == {
        'sources': {
            'eats': {
                'passport_uids': [
                    '1123354197',
                    '1217368748',
                    '1337736745',
                    '1347795374',
                    '1525675487',
                    '1526155166',
                    '675986992',
                    '789374070',
                    '793470429',
                    '798853027',
                    '813175221',
                    '867327636',
                    '867665402',
                    '870563279',
                    '899534391',
                    '900808934',
                ],
            },
            'grocery': {
                'passport_uids': [
                    '1123354197',
                    '1217368748',
                    '1337736745',
                    '1347795374',
                    '1525675487',
                    '1526155166',
                    '675986992',
                    '789374070',
                    '793470429',
                    '798853027',
                    '813175221',
                    '867327636',
                    '867665402',
                    '870563279',
                    '899534391',
                    '900808934',
                ],
            },
            'taxi': {'passport_uids': ['1', '2']},
        },
    }
