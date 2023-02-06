import pytest

from taxi_admin_personal.data_access import from_mongo


@pytest.mark.parametrize(
    'value,expected',
    [
        ('0000098000', {'643753730324_69aa324ee0d24ae583dae31f365bf63b'}),
        (
            '00000000000',
            {
                '100900_3580371a802b4c5b911ff3e0c0196244',
                '100112_ca3a2377daf2440097e2b9ec9749ca28',
                '643753730335_b268d6727a7840ed9ca6dee4f5919c12',
                '100500_794513c94b864ad7ad1088063ec468e1',
            },
        ),
    ],
)
async def test_search_drivers_by_pda_license(db, value, expected):
    assert (
        set(await from_mongo.search_drivers_by_pda_license(db, value))
        == expected
    )


@pytest.mark.parametrize(
    'value,expected',
    [
        (
            '+79000000000',
            {
                '100500_3625641848644387a263e78b2c3a7a5c',
                '100500_794513c94b864ad7ad1088063ec468e1',
            },
        ),
        (
            '+79000000014',
            {
                '100500_63a30c2584354146a65bf9e01c555a4c',
                '100112_ca3a2377daf2440097e2b9ec9749ca28',
                '100400_08d2d920ed9a4b138ced811d2bff5498',
            },
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'taxi-admin-personal', 'dst': 'personal'}],
)
async def test_search_drivers_by_pda_phone(
        web_context, db, value, expected, mock_countries, mock_pd_phones,
):
    assert (
        set(
            await from_mongo.search_drivers_by_pda_phone(
                db, value, web_context,
            ),
        )
        == expected
    )

    assert mock_pd_phones.bulk_find_count == 1


@pytest.mark.parametrize(
    'driver_id,field,expected',
    [
        ('100500_3625641848644387a263e78b2c3a7a5c', 'phone', '+79000000000'),
        (
            '5192573621_f977c37e2653e61186a6001e671f718d',
            'phone',
            '+79000000005',
        ),
        ('100400_08d2d920ed9a4b138ced811d2bff5498', 'phone', '+79000000014'),
        (
            '100500_794513c94b864ad7ad1088063ec468e1',
            'driver_license',
            '00000000000',
        ),
        (
            '643753730324_69aa324ee0d24ae583dae31f365bf63b',
            'driver_license',
            '0000098000',
        ),
        (
            '5192573621_f977c37e2653e61186a6001e671f718d',
            'driver_license',
            '0000000000',
        ),
        (
            '100400_08d2d920ed9a4b138ced811d2bff5498',
            'driver_license',
            '0000088888',
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'taxi-admin-personal', 'dst': 'personal'}],
)
async def test_get_driver_pd_field(
        web_context,
        db,
        driver_id,
        field,
        expected,
        mock_countries,
        mock_pd_phones,
):
    assert (
        await from_mongo.get_driver_pd_field(db, field, driver_id, web_context)
    ) == expected

    if field == 'phone':
        assert mock_pd_phones.bulk_retrieve_count == 1
