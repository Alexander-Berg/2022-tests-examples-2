from psycopg2 import extras


CORE_PICKERS_RESPONSE = {
    'payload': {
        'pickers': [
            {
                'id': 1,
                'phone_id': '2',
                'name': 'Петров Пётр Петрович',
                'available_until': '2020-10-08T14:00:00+0300',
                'available_places': [1, 2, 3],
                'requisite_type': 'TinkoffCard',
                'requisite_value': '1234567890',
            },
            {
                'id': 2,
                'phone_id': '3',
                'name': 'Сидоров Пётр Петрович',
                'available_until': '2020-10-08T14:00:00+0300',
                'available_places': [1, 2, 3, 4],
                'requisite_type': 'TinkoffCard',
                'requisite_value': '0987654321',
            },
        ],
    },
}


async def test_pickers_synchronizer_initial(
        mockserver, testpoint, pgsql, taxi_eats_picker_supply,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/eats-core/v1/supply/pickers-list')
    def eats_core(request):
        return CORE_PICKERS_RESPONSE

    @testpoint('eats_picker_supply::pickers-synchronizer')
    def handle_finished(arg):
        pass

    await taxi_eats_picker_supply.run_distlock_task('pickers-synchronizer')
    handle_finished.next_call()
    pg_cursor = pgsql['eats_picker_supply'].cursor(
        cursor_factory=extras.RealDictCursor,
    )
    pg_cursor.execute(
        'select * from eats_picker_supply.pickers order by picker_id;',
    )
    rows = pg_cursor.fetchall()
    assert len(rows) == 2


async def test_pickers_synchronizer(
        mockserver, testpoint, pgsql, taxi_eats_picker_supply, create_picker,
):
    create_picker(
        picker_id=1,
        name='Иванов Иван Иванович',
        phone_id='1',
        places_ids=[1],
        requisite_type='TinkoffCard',
        requisite_value='1234567890',
    )
    create_picker(
        picker_id=3,
        name='Иванов Пётр Иванович',
        phone_id='4',
        places_ids=[1],
        requisite_type='TinkoffCard',
        requisite_value='1029384756',
    )

    # pylint: disable=unused-variable
    @mockserver.json_handler('/eats-core/v1/supply/pickers-list')
    def eats_core(request):
        return CORE_PICKERS_RESPONSE

    @testpoint('eats_picker_supply::pickers-synchronizer')
    def handle_finished(arg):
        pass

    await taxi_eats_picker_supply.run_distlock_task('pickers-synchronizer')
    handle_finished.next_call()
    pg_cursor = pgsql['eats_picker_supply'].cursor(
        cursor_factory=extras.RealDictCursor,
    )
    pg_cursor.execute(
        'select * from eats_picker_supply.pickers order by picker_id;',
    )
    rows = pg_cursor.fetchall()
    assert len(rows) == 2

    assert rows[0]['name'] == 'Петров Пётр Петрович'
    assert rows[0]['phone_id'] == '2'
    assert rows[0]['requisite_type'] == 'TinkoffCard'
    assert rows[0]['requisite_value'] == '1234567890'
    assert rows[0]['places_ids'] == [1, 2, 3]
    assert rows[0]['created_at'] != rows[0]['updated_at']

    assert rows[1]['name'] == 'Сидоров Пётр Петрович'
    assert rows[1]['phone_id'] == '3'
    assert rows[1]['requisite_type'] == 'TinkoffCard'
    assert rows[1]['requisite_value'] == '0987654321'
    assert rows[1]['places_ids'] == [1, 2, 3, 4]
