def select_accumulators_info(
        pgsql,
        accumulator_id=None,
        select_charge=False,
        select_serial_number=False,
        serial_number=None,
):
    db = pgsql['scooter_accumulator'].cursor()
    select_str = (
        'SELECT accumulator_id, contractor_id, cabinet_id, scooter_id '
    )

    if serial_number:
        db.execute(
            'SELECT accumulator_id '
            'FROM scooter_accumulator.accumulators '
            f'WHERE accumulators.serial_number = \'{serial_number}\';',
        )
        accumulators_by_serial_number = db.fetchall()
        if accumulators_by_serial_number:
            accumulator_id = accumulators_by_serial_number[0][0]

    if select_charge:
        select_str += ', charge '

    if select_serial_number:
        select_str += ', serial_number '

    db.execute(
        f'{select_str}'
        'FROM scooter_accumulator.accumulators '
        'ORDER BY accumulator_id ASC;',
    )

    accumulators = db.fetchall()
    if not (accumulator_id or serial_number):
        return accumulators

    for accumulator in accumulators:
        if accumulator[0] == accumulator_id:
            return [accumulator]

    return [()]


def select_cells_info(
        pgsql,
        cell_id=None,
        select_is_open=False,
        select_error_code=False,
        select_error_response_number=False,
):
    db = pgsql['scooter_accumulator'].cursor()

    select_str = 'SELECT cell_id, accumulator_id, booked_by '
    if select_is_open:
        select_str += ', is_open '
    if select_error_code:
        select_str += ', error_code '
    if select_error_response_number:
        select_str += ', error_response_number '

    db.execute(
        f'{select_str}'
        'FROM scooter_accumulator.cells '
        'ORDER BY cell_id ASC, cabinet_id ASC;',
    )

    cells = db.fetchall()
    if not cell_id:
        return cells

    for cell in cells:
        if cell[0] == cell_id:
            return [cell]

    return [()]


def select_cells_by_cabinet(pgsql, cabinet_id):
    db = pgsql['scooter_accumulator'].cursor()

    db.execute(
        'SELECT cabinet_id, cell_id, accumulator_id, booked_by '
        'FROM scooter_accumulator.cells '
        f'WHERE cells.cabinet_id = \'{cabinet_id}\' '
        'ORDER BY CAST(cell_id AS integer) ASC;',
    )

    return db.fetchall()


def select_bookings_info(
        pgsql, booking_id=None, select_cell_id=False, select_comment=False,
):
    db = pgsql['scooter_accumulator'].cursor()

    select_str = (
        'SELECT booking_id, booking_status, contractor_id, accumulator_id '
    )
    if select_cell_id:
        select_str += ', cell_id '

    if select_comment:
        select_str += ', comment '

    db.execute(
        f'{select_str}'
        'FROM scooter_accumulator.bookings '
        'ORDER BY booking_id ASC;',
    )

    bookings = db.fetchall()
    if not booking_id:
        return bookings

    for booking in bookings:
        if booking[0] == booking_id:
            return [booking]

    return [()]


def select_cabinets_info(
        pgsql,
        cabinet_id=None,
        depot_id=False,
        cabinet_type=False,
        cabinet_name=False,
):
    db = pgsql['scooter_accumulator'].cursor()

    select_str = 'SELECT cabinet_id '

    if depot_id:
        select_str += ', depot_id '

    if cabinet_type:
        select_str += ', type '

    if cabinet_name:
        select_str += ', cabinet_name '

    db.execute(
        f'{select_str}'
        'FROM scooter_accumulator.cabinets '
        'ORDER BY cabinet_id ASC;',
    )

    cabinets = db.fetchall()
    if not cabinet_id:
        return cabinets

    for cabinet in cabinets:
        if cabinet[0] == cabinet_id:
            return [cabinet]

    return [()]
