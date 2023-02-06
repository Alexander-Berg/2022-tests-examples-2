from tests_driver_mode_subscription import driver


# Creates booking reservation of a slot for a driver query
#  (only use this if driver had no reservation
#   on this particular slot before)
def reserve(slot: str, driver_profile: driver.Profile):
    upsert_query = (
        f'INSERT INTO booking.slots (name, count) '
        f'VALUES (\'{slot}\', 1) ON CONFLICT (name) DO UPDATE '
        f'SET count = EXCLUDED.count + 1 RETURNING id'
    )
    return (
        f'WITH slot AS ({upsert_query}) '
        f'INSERT INTO booking.slot_reservations (slot_id, issuer) '
        f'VALUES ((SELECT id FROM slot), \'{driver_profile.dbid_uuid()}\')'
    )


def insert_slot(pgsql, name: str, slot_id: int, count: int = 0):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        f'INSERT INTO booking.slots (id, name, count) '
        f'VALUES ({slot_id}, \'{name}\', {count})',
    )


def make_reservation(pgsql, slot_id: int, driver_profile: driver.Profile):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        f'INSERT INTO booking.slot_reservations (slot_id, issuer) '
        f'VALUES ({slot_id}, \'{driver_profile.dbid_uuid()}\')',
    )


def remove_reservations(pgsql, driver_profile: driver.Profile):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        f'DELETE FROM booking.slot_reservations WHERE '
        f'issuer = \'{driver_profile.dbid_uuid()}\'',
    )


# Performs request to get all current driver's booking reservations
def get_reservations(pgsql, driver_profile: driver.Profile):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        f'SELECT name as slot FROM booking.slots s '
        f'INNER JOIN booking.slot_reservations r ON s.id=r.slot_id '
        f'WHERE r.issuer = \'{driver_profile.dbid_uuid()}\'',
    )
    rows = list(row for row in cursor)
    return rows
