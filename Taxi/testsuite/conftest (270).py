# pylint: disable=redefined-outer-name
import pytest


pytest_plugins = ['eats_picker_racks_plugins.pytest_plugins']


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_picker_racks'].dict_cursor()

    return create_cursor


@pytest.fixture()
def create_place(get_cursor):
    def do_create_place(
            place_id: int = 1,
            name: str = 'first place',
            address: str = 'first address',
            brand_id: int = None,
            brand_name: str = None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_racks.places '
            '(place_id, name, address, brand_id, brand_name) '
            'VALUES (%s, %s, %s, %s, %s) '
            'RETURNING place_id',
            [place_id, name, address, brand_id, brand_name],
        )
        return cursor.fetchone()

    return do_create_place


@pytest.fixture()
def get_place(get_cursor):
    def do_get_place(place_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_racks.places WHERE place_id = %s',
            [place_id],
        )
        return cursor.fetchone()

    return do_get_place


@pytest.fixture()
def create_rack(get_cursor):
    def do_create_rack(
            place_id: int = 1,
            name: str = 'first',
            description: str = 'some description',
            has_fridge: bool = None,
            has_freezer: bool = None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_racks.racks '
            '(place_id, name, description, has_fridge, has_freezer) '
            'VALUES (%s, %s, %s, %s, %s) '
            'RETURNING id',
            [place_id, name, description, has_fridge, has_freezer],
        )
        return cursor.fetchone()

    return do_create_rack


@pytest.fixture()
def create_cell(get_cursor):
    def do_create_cell(rack_id: int = 1):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_racks.cells '
            '(rack_id, number) '
            '(SELECT %(rack_id)s, COALESCE(MAX(number) + 1, 1) '
            'FROM eats_picker_racks.cells '
            'WHERE rack_id = %(rack_id)s) '
            'RETURNING id, number',
            {'rack_id': rack_id},
        )
        return cursor.fetchone()

    return do_create_cell


@pytest.fixture()
def put_order_packets(get_cursor):
    def do_put_order_packets(
            rack_id: int = 1,
            cell_number: int = 1,
            eats_id: str = '1',
            packets_number: int = 1,
            picker_id: str = '1',
            rack_name: str = 'first',
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_racks.orders_packages '
            '(cell_id, eats_id, packets_number, picker_id,'
            ' cell_number, rack_id, rack_name) '
            '(SELECT cells.id, %s, %s, %s, %s, %s, %s '
            'FROM eats_picker_racks.cells '
            'WHERE cells.rack_id = %s AND cells.number = %s)',
            [
                eats_id,
                packets_number,
                picker_id,
                cell_number,
                rack_id,
                rack_name,
                rack_id,
                cell_number,
            ],
        )

    return do_put_order_packets


@pytest.fixture()
def get_cells_in_rack(get_cursor):
    def do_get_order(rack_id: int = 1):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_racks.cells WHERE rack_id = %s',
            [rack_id],
        )
        return cursor.fetchall()

    return do_get_order


@pytest.fixture()
def get_packets_in_rack(get_cursor):
    def do_get_order(rack_id: int = 1):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_racks.orders_packages '
            'JOIN eats_picker_racks.cells '
            'ON cells.id = orders_packages.cell_id '
            'WHERE cells.rack_id = %s',
            [rack_id],
        )
        return cursor.fetchall()

    return do_get_order


@pytest.fixture()
def get_packets_in_cell(get_cursor):
    def do_get_order(cell_id: int = 1):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_racks.orders_packages '
            'WHERE cell_id = %s',
            [cell_id],
        )
        return cursor.fetchall()

    return do_get_order


@pytest.fixture()
def init_postgresql(create_place, create_rack, create_cell, put_order_packets):
    create_place(1, 'first place', 'first address')
    create_place(2, 'second place', 'second address')
    create_rack(1, 'first')
    create_rack(1, 'second', None)
    create_rack(2, 'third', None)
    create_cell(1)
    create_cell(1)
    create_cell(1)
    create_cell(2)
    create_cell(3)
    put_order_packets(
        rack_id=1,
        cell_number=1,
        eats_id='1',
        packets_number=1,
        picker_id='1',
        rack_name='first',
    )
    put_order_packets(
        rack_id=2,
        cell_number=1,
        eats_id='1',
        packets_number=2,
        picker_id='1',
        rack_name='second',
    )
    put_order_packets(
        rack_id=1,
        cell_number=1,
        eats_id='2',
        packets_number=2,
        picker_id='2',
        rack_name='first',
    )
    put_order_packets(
        rack_id=1,
        cell_number=1,
        eats_id='4',
        packets_number=1,
        picker_id='2',
        rack_name='first',
    )
    put_order_packets(
        rack_id=3,
        cell_number=1,
        eats_id='4',
        packets_number=2,
        picker_id='2',
        rack_name='second',
    )
