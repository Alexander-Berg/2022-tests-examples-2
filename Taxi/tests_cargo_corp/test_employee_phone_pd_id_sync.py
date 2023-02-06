import pytest

from tests_cargo_corp import utils


(
    LOCAL_CORP_ID0,
    LOCAL_CORP_ID1,
    LOCAL_CORP_ID2,
    LOCAL_CORP_ID3,
    LOCAL_CORP_ID4,
) = (
    utils.CORP_CLIENT_ID,  # effects due autouse fixture
    'corp_client_id_12345678910111213',
    'corp_client_id_12345678910111214',
    'corp_client_id_12345678910111215',
    'corp_client_id_12345678910111216',
)

EMPLOYEE_PHONE_CHANGES_START = [
    (1, 'corp_client_id_12345678910111213', 'yandex_uid1', None, '11'),
    (2, 'corp_client_id_12345678910111213', 'yandex_uid2', None, '12'),
    (3, 'corp_client_id_12345678910111213', 'yandex_uid3', None, '13'),
    (4, 'corp_client_id_12345678910111213', 'yandex_uid4', None, '14'),
    (5, 'corp_client_id_12345678910111213', 'yandex_uid5', None, '15'),
    (6, 'corp_client_id_12345678910111214', 'yandex_uid1', None, '21'),
    (7, 'corp_client_id_12345678910111214', 'yandex_uid2', None, '22'),
    (8, 'corp_client_id_12345678910111214', 'yandex_uid3', None, '23'),
    (9, 'corp_client_id_12345678910111214', 'yandex_uid4', None, '24'),
    (10, 'corp_client_id_12345678910111214', 'yandex_uid5', None, '25'),
    (11, 'corp_client_id_12345678910111215', 'yandex_uid1', None, '31'),
    (12, 'corp_client_id_12345678910111215', 'yandex_uid2', None, '32'),
    (13, 'corp_client_id_12345678910111215', 'yandex_uid3', None, '33'),
    (14, 'corp_client_id_12345678910111215', 'yandex_uid4', None, '34'),
    (15, 'corp_client_id_12345678910111215', 'yandex_uid5', None, '35'),
    (16, 'corp_client_id_12345678910111216', 'yandex_uid1', None, '41'),
    (17, 'corp_client_id_12345678910111216', 'yandex_uid2', None, '42'),
    (18, 'corp_client_id_12345678910111216', 'yandex_uid3', None, '43'),
    (19, 'corp_client_id_12345678910111216', 'yandex_uid4', None, '44'),
    (20, 'corp_client_id_12345678910111216', 'yandex_uid5', None, '45'),
    (
        21,
        'corp_client_id_1_______32symbols',
        'yandex_uid1',
        None,
        '87776667766_id',
    ),
]
EMPLOYEES_PHONE_PD_IDS_EXPECTED_DATA = [
    ('11', 3596227959, 'yandex_uid1', LOCAL_CORP_ID1),
    ('12', 1330857165, 'yandex_uid2', LOCAL_CORP_ID1),
    ('13', 945058907, 'yandex_uid3', LOCAL_CORP_ID1),
    ('14', 2788221432, 'yandex_uid4', LOCAL_CORP_ID1),
    ('15', 3510096238, 'yandex_uid5', LOCAL_CORP_ID1),
    ('21', 4252452532, 'yandex_uid1', LOCAL_CORP_ID2),
    ('22', 1685985038, 'yandex_uid2', LOCAL_CORP_ID2),
    ('23', 326707096, 'yandex_uid3', LOCAL_CORP_ID2),
    ('24', 2367533627, 'yandex_uid4', LOCAL_CORP_ID2),
    ('25', 4196041389, 'yandex_uid5', LOCAL_CORP_ID2),
    ('31', 3832313845, 'yandex_uid1', LOCAL_CORP_ID3),
    ('32', 2103780943, 'yandex_uid2', LOCAL_CORP_ID3),
    ('33', 174200537, 'yandex_uid3', LOCAL_CORP_ID3),
    ('34', 2483454842, 'yandex_uid4', LOCAL_CORP_ID3),
    ('35', 3808539628, 'yandex_uid5', LOCAL_CORP_ID3),
    ('41', 2871910706, 'yandex_uid1', LOCAL_CORP_ID4),
    ('42', 841265288, 'yandex_uid2', LOCAL_CORP_ID4),
    ('43', 1159954462, 'yandex_uid3', LOCAL_CORP_ID4),
    ('44', 3678868925, 'yandex_uid4', LOCAL_CORP_ID4),
    ('45', 2889884971, 'yandex_uid5', LOCAL_CORP_ID4),
    (
        '87776667766_id',
        1059062347,
        'yandex_uid1',
        'corp_client_id_1_______32symbols',
    ),
]

EMPLOYEE_PHONE_CHANGES_CUT = [
    (22, 'corp_client_id_12345678910111213', 'yandex_uid1', '11', None),
    (23, 'corp_client_id_12345678910111213', 'yandex_uid2', '12', None),
    (24, 'corp_client_id_12345678910111213', 'yandex_uid3', '13', None),
    (25, 'corp_client_id_12345678910111213', 'yandex_uid4', '14', None),
    (26, 'corp_client_id_12345678910111213', 'yandex_uid5', '15', None),
    (27, 'corp_client_id_12345678910111214', 'yandex_uid1', '21', None),
    (28, 'corp_client_id_12345678910111214', 'yandex_uid2', '22', None),
    (29, 'corp_client_id_12345678910111214', 'yandex_uid3', '23', None),
    (30, 'corp_client_id_12345678910111214', 'yandex_uid4', '24', None),
    (31, 'corp_client_id_12345678910111214', 'yandex_uid5', '25', None),
    (32, 'corp_client_id_12345678910111215', 'yandex_uid1', '31', None),
    (33, 'corp_client_id_12345678910111215', 'yandex_uid5', '35', None),
    (34, 'corp_client_id_12345678910111216', 'yandex_uid1', '41', None),
    (35, 'corp_client_id_12345678910111216', 'yandex_uid5', '45', None),
    (
        36,
        'corp_client_id_1_______32symbols',
        'yandex_uid1',
        '87776667766_id',
        None,
    ),
]
EMPLOYEES_PHONE_PD_IDS_EXPECTED_DATA_CUT = [
    ('32', 2103780943, 'yandex_uid2', LOCAL_CORP_ID3),
    ('33', 174200537, 'yandex_uid3', LOCAL_CORP_ID3),
    ('34', 2483454842, 'yandex_uid4', LOCAL_CORP_ID3),
    ('42', 841265288, 'yandex_uid2', LOCAL_CORP_ID4),
    ('43', 1159954462, 'yandex_uid3', LOCAL_CORP_ID4),
    ('44', 3678868925, 'yandex_uid4', LOCAL_CORP_ID4),
]

EMPLOYEE_PHONE_CHANGES_CUT_UPDATE = [
    (37, 'corp_client_id_12345678910111215', 'yandex_uid2', '32', '777'),
    (38, 'corp_client_id_12345678910111216', 'yandex_uid2', '42', '777'),
    (39, 'corp_client_id_12345678910111213', 'yandex_uid2', '12', None),
    (40, 'corp_client_id_12345678910111214', 'yandex_uid2', '22', None),
]
EMPLOYEES_PHONE_PD_IDS_EXPECTED_DATA_CUT_UPDATE = [
    ('33', 174200537, 'yandex_uid3', LOCAL_CORP_ID3),
    ('34', 2483454842, 'yandex_uid4', LOCAL_CORP_ID3),
    ('43', 1159954462, 'yandex_uid3', LOCAL_CORP_ID4),
    ('44', 3678868925, 'yandex_uid4', LOCAL_CORP_ID4),
    ('777', 4141821756, 'yandex_uid2', LOCAL_CORP_ID3),
    ('777', 4141821756, 'yandex_uid2', LOCAL_CORP_ID4),
]

EMPLOYEE_PHONE_CHANGES_CUT_UPDATE_UPDATE = [
    (41, 'corp_client_id_12345678910111215', 'yandex_uid2', '777', '888'),
    (42, 'corp_client_id_12345678910111216', 'yandex_uid2', '777', '888'),
    (43, 'corp_client_id_12345678910111213', 'yandex_uid2', '777', None),
    (44, 'corp_client_id_12345678910111214', 'yandex_uid2', '777', None),
    (45, 'corp_client_id_12345678910111215', 'yandex_uid2', '888', '999'),
    (46, 'corp_client_id_12345678910111216', 'yandex_uid2', '888', '999'),
    (47, 'corp_client_id_12345678910111213', 'yandex_uid2', '888', None),
    (48, 'corp_client_id_12345678910111214', 'yandex_uid2', '888', None),
]
EMPLOYEES_PHONE_PD_IDS_EXPECTED_DATA_CUT_UPDATE_UPDATE = [
    ('33', 174200537, 'yandex_uid3', LOCAL_CORP_ID3),
    ('34', 2483454842, 'yandex_uid4', LOCAL_CORP_ID3),
    ('43', 1159954462, 'yandex_uid3', LOCAL_CORP_ID4),
    ('44', 3678868925, 'yandex_uid4', LOCAL_CORP_ID4),
    ('999', 2239365823, 'yandex_uid2', LOCAL_CORP_ID3),
    ('999', 2239365823, 'yandex_uid2', LOCAL_CORP_ID4),
]


async def run_sync(cursor, run_employee_phone_pd_id_sync, worker_list=None):
    if worker_list is not None:
        cursor.execute(
            f"""
            SELECT id,corp_client_id,yandex_uid,old_phone,new_phone
            FROM corp_clients.employee_phone_changes;
            """,
        )
        assert list(cursor) == worker_list
    await run_employee_phone_pd_id_sync()
    cursor.execute(
        f"""
        SELECT id,corp_client_id,yandex_uid,old_phone,new_phone
        FROM corp_clients.employee_phone_changes;
        """,
    )
    assert list(cursor) == []


@pytest.mark.config(
    CARGO_CORP_EMPLOYEE_PHONE_ID_SYNC_SETTINGS={'enabled': True},
)
@pytest.mark.pgsql(
    'cargo_corp',
    queries=[
        f"""
        INSERT INTO corp_clients.clients
        (corp_client_id, sharded_key_hash)
        VALUES
        ('{LOCAL_CORP_ID1}', 1),
        ('{LOCAL_CORP_ID2}', 2),
        ('{LOCAL_CORP_ID3}', 3),
        ('{LOCAL_CORP_ID4}', 4);
        """,
        f"""
        INSERT INTO corp_clients.employees
        (corp_client_id, yandex_uid, phone_pd_ids)
        VALUES
        ('{LOCAL_CORP_ID1}', 'yandex_uid1', '{{"11"}}'::TEXT[]),
        ('{LOCAL_CORP_ID1}', 'yandex_uid2', '{{"12"}}'::TEXT[]),
        ('{LOCAL_CORP_ID1}', 'yandex_uid3', '{{"13"}}'::TEXT[]),
        ('{LOCAL_CORP_ID1}', 'yandex_uid4', '{{"14"}}'::TEXT[]),
        ('{LOCAL_CORP_ID1}', 'yandex_uid5', '{{"15"}}'::TEXT[]),
        ('{LOCAL_CORP_ID2}', 'yandex_uid1', '{{"21"}}'::TEXT[]),
        ('{LOCAL_CORP_ID2}', 'yandex_uid2', '{{"22"}}'::TEXT[]),
        ('{LOCAL_CORP_ID2}', 'yandex_uid3', '{{"23"}}'::TEXT[]),
        ('{LOCAL_CORP_ID2}', 'yandex_uid4', '{{"24"}}'::TEXT[]),
        ('{LOCAL_CORP_ID2}', 'yandex_uid5', '{{"25"}}'::TEXT[]),
        ('{LOCAL_CORP_ID3}', 'yandex_uid1', '{{"31"}}'::TEXT[]),
        ('{LOCAL_CORP_ID3}', 'yandex_uid2', '{{"32"}}'::TEXT[]),
        ('{LOCAL_CORP_ID3}', 'yandex_uid3', '{{"33"}}'::TEXT[]),
        ('{LOCAL_CORP_ID3}', 'yandex_uid4', '{{"34"}}'::TEXT[]),
        ('{LOCAL_CORP_ID3}', 'yandex_uid5', '{{"35"}}'::TEXT[]),
        ('{LOCAL_CORP_ID4}', 'yandex_uid1', '{{"41"}}'::TEXT[]),
        ('{LOCAL_CORP_ID4}', 'yandex_uid2', '{{"42"}}'::TEXT[]),
        ('{LOCAL_CORP_ID4}', 'yandex_uid3', '{{"43"}}'::TEXT[]),
        ('{LOCAL_CORP_ID4}', 'yandex_uid4', '{{"44"}}'::TEXT[]),
        ('{LOCAL_CORP_ID4}', 'yandex_uid5', '{{"45"}}'::TEXT[]);
        """,
    ],
)
async def test_sync_with_secondary(
        run_employee_phone_pd_id_sync, user_has_rights, pgsql,
):
    cursor = pgsql['cargo_corp'].cursor()
    await run_sync(
        cursor, run_employee_phone_pd_id_sync, EMPLOYEE_PHONE_CHANGES_START,
    )

    cursor.execute(
        """
        SELECT * FROM employees_phone_pd_ids.employees
        ORDER BY phone_pd_id;
        """,
    )
    assert list(cursor) == EMPLOYEES_PHONE_PD_IDS_EXPECTED_DATA

    cursor.execute(
        f"""
        UPDATE corp_clients.employees
        SET is_disabled = TRUE
        WHERE
        corp_client_id IN ('{LOCAL_CORP_ID1}', '{LOCAL_CORP_ID2}')
        OR yandex_uid IN ('yandex_uid1', 'yandex_uid5');
        """,
    )
    await run_sync(
        cursor, run_employee_phone_pd_id_sync, EMPLOYEE_PHONE_CHANGES_CUT,
    )

    cursor.execute(
        """
        SELECT * FROM employees_phone_pd_ids.employees
        ORDER BY phone_pd_id;
        """,
    )
    assert list(cursor) == EMPLOYEES_PHONE_PD_IDS_EXPECTED_DATA_CUT

    cursor.execute(
        f"""
        UPDATE corp_clients.employees
        SET phone_pd_ids = '{{"777"}}'::TEXT[]
        WHERE yandex_uid = 'yandex_uid2';
        """,
    )
    await run_sync(
        cursor,
        run_employee_phone_pd_id_sync,
        EMPLOYEE_PHONE_CHANGES_CUT_UPDATE,
    )

    cursor.execute(
        """
        SELECT * FROM employees_phone_pd_ids.employees
        ORDER BY phone_pd_id;
        """,
    )
    assert list(cursor) == EMPLOYEES_PHONE_PD_IDS_EXPECTED_DATA_CUT_UPDATE

    cursor.execute(
        f"""
        UPDATE corp_clients.employees
        SET phone_pd_ids = '{{"888"}}'::TEXT[]
        WHERE yandex_uid = 'yandex_uid2';
        """,
    )
    cursor.execute(
        f"""
        UPDATE corp_clients.employees
        SET phone_pd_ids = '{{"999"}}'::TEXT[]
        WHERE yandex_uid = 'yandex_uid2';
        """,
    )
    await run_sync(
        cursor,
        run_employee_phone_pd_id_sync,
        EMPLOYEE_PHONE_CHANGES_CUT_UPDATE_UPDATE,
    )

    cursor.execute(
        """
        SELECT * FROM employees_phone_pd_ids.employees
        ORDER BY phone_pd_id;
        """,
    )
    assert (
        list(cursor) == EMPLOYEES_PHONE_PD_IDS_EXPECTED_DATA_CUT_UPDATE_UPDATE
    )
