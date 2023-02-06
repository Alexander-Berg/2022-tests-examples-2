async def test_initialize(taxi_contractor_profession, pgsql):
    response = await taxi_contractor_profession.post(
        '/internal/v1/professions/initialize-contractors',
        params={'consumer': 'test_consumer'},
        json={
            'ids': [
                {
                    'park_id': 'park_id',
                    'contractor_profile_id': 'contractor_profile_id',
                    'profession_id': 'taxi-driver',
                },
                {
                    'park_id': 'park_id',
                    'contractor_profile_id': 'contractor_profile_id',
                    'profession_id': 'auto-courier',
                },
            ],
        },
    )

    assert response.status_code == 200

    cursor = pgsql['contractor_profession'].cursor()
    cursor.execute(
        """SELECT increment, park_id, contractor_id, profession_id, source
        FROM contractor_profession.professions_changelog
        ORDER BY increment
        """,
    )
    result = list(cursor)
    assert result == [
        (
            1,
            'park_id',
            'contractor_profile_id',
            'taxi-driver',
            'initial:test_consumer',
        ),
    ]

    cursor.execute(
        """SELECT park_id, contractor_id, profession_id, increment
        FROM contractor_profession.professions
        ORDER BY increment
        """,
    )
    result = list(cursor)
    assert result == [('park_id', 'contractor_profile_id', 'taxi-driver', 1)]
