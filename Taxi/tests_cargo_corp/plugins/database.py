from typing import List
from typing import Optional
import uuid

import pytest

from tests_cargo_corp import utils


@pytest.fixture(autouse=True)
def corp_client(pgsql):
    utils.create_client(pgsql)


@pytest.fixture()
def user_has_rights(pgsql):
    utils.create_role(
        pgsql,
        role_name=utils.OWNER_ROLE,
        permission_ids=utils.ALL_PERMISSION_IDS,
        corp_client_id=None,
        role_id=utils.ROLE_ID,
    )
    utils.create_employee(pgsql, yandex_uid=utils.YANDEX_UID)
    utils.create_employee_role(
        pgsql, utils.ROLE_ID, yandex_uid=utils.YANDEX_UID,
    )


@pytest.fixture()
def register_default_user(pgsql):
    utils.register_employee(pgsql)


@pytest.fixture(name='create_role')
def _create_role(pgsql):
    def wrapper(
            is_removable=True,
            permission_ids=utils.ALL_PERMISSION_IDS,
            role_name=utils.OWNER_ROLE,
            is_removed=False,
            corp_client_id=utils.CORP_CLIENT_ID,
            role_id=None,
    ):
        return utils.create_role(
            pgsql,
            is_removable,
            permission_ids,
            role_name,
            is_removed,
            corp_client_id,
            role_id,
        )

    return wrapper


@pytest.fixture(name='remove_role')
def _remove_role(pgsql):
    def wrapper(role_id):
        utils.remove_role(pgsql, role_id)

    return wrapper


@pytest.fixture(name='create_employee_candidate')
def _create_employee_candidate(pgsql):
    def wrapper(
            confirmation_code='test_confirmation_code',
            name='test_employee_candidate',
            corp_client_id=utils.CORP_CLIENT_ID,
            phone_pd_id='1234567890_id',
            role_id=None,
            email_pd_id='test@ya.ru',
            revision=1,
    ):
        return utils.create_employee_candidate(
            pgsql,
            confirmation_code,
            name,
            corp_client_id,
            phone_pd_id,
            role_id,
            revision,
        )

    return wrapper


@pytest.fixture()
def get_employee_candidate_info(pgsql):
    def wrapper(
            confirmation_code='test_confirmation_code',
            corp_client_id=utils.CORP_CLIENT_ID,
    ):
        return utils.get_employee_candidate_info(
            pgsql, confirmation_code, corp_client_id,
        )

    return wrapper


@pytest.fixture()
def get_client_by_id(pgsql):
    def wrapper(corp_client_id=utils.CORP_CLIENT_ID):
        return utils.get_client_by_id(pgsql, corp_client_id)

    return wrapper


@pytest.fixture(name='get_client_extra_info')
def _get_client_extra_info(pgsql):
    def wrapper(corp_client_id):
        return utils.get_client_extra_info(pgsql, corp_client_id)

    return wrapper


@pytest.fixture(name='get_client_balance_info')
def _get_client_balance_info(pgsql):
    def wrapper(corp_client_id):
        return utils.get_client_balance_info(pgsql, corp_client_id)

    return wrapper


# creates passed corp_clients, employee
# and assigns employee to all clients
@pytest.fixture(name='prepare_multiple_clients')
def _prepare_db(pgsql):
    def wrapper(
            corp_clients,
            yandex_uid=utils.YANDEX_UID,
            phone_pd_id=utils.PHONE_PD_ID,
            yandex_login_pd_id=utils.YANDEX_LOGIN_PD_ID,
            card_id=None,
            is_robot=False,
    ):
        for client in corp_clients:
            if 'employee' in client:
                employee = client['employee']
                if 'phone_pd_id' in employee:
                    phone_pd_id = employee['phone_pd_id']
                if 'yandex_login_pd_id' in employee:
                    yandex_login_pd_id = employee['yandex_login_pd_id']

            utils.create_client(
                pgsql,
                corp_client_id=client['id'],
                corp_client_name=client['name'],
                is_registered=client['is_registration_finished'],
            )
            utils.create_employee(
                pgsql,
                yandex_uid=yandex_uid,
                corp_client_id=client['id'],
                phone_pd_id=phone_pd_id,
                yandex_login_pd_id=yandex_login_pd_id,
                is_robot=is_robot,
            )

            utils.register_employee(
                pgsql,
                corp_client_id=client['id'],
                yandex_uid=yandex_uid,
                phone_pd_id=phone_pd_id,
            )

            if card_id is not None:
                utils.add_card(
                    pgsql,
                    corp_client_id=client['id'],
                    yandex_uid=yandex_uid,
                    card_id=card_id,
                )

    return wrapper


@pytest.fixture(name='select_employee')
async def _select_employee(pgsql):
    def wrapper(*, corp_client_id: str, yandex_uid: str):
        with pgsql['cargo_corp'].dict_cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM corp_clients.employees
                WHERE corp_client_id = %s AND yandex_uid = %s
                """,
                (corp_client_id, yandex_uid),
            )

            assert cursor.rowcount <= 1

            if cursor.rowcount == 0:
                return cursor.fetchone()

            return dict(cursor.fetchone())

    return wrapper


@pytest.fixture(name='select_cards')
async def _select_cards(pgsql):
    def wrapper(*, corp_client_id: str, yandex_uid: str):
        with pgsql['cargo_corp'].dict_cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM corp_clients.bound_cards
                WHERE corp_client_id = %s AND yandex_uid = %s
                """,
                (corp_client_id, yandex_uid),
            )

            return [dict(r) for r in cursor.fetchall()]

    return wrapper


@pytest.fixture(name='insert_card')
async def _insert_card(pgsql):
    def wrapper(*, corp_client_id: str, yandex_uid: str, card_id: str):
        with pgsql['cargo_corp'].dict_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO corp_clients.bound_cards
                (corp_client_id,yandex_uid,card_id,is_bound)
                VALUES(%s,%s,%s,TRUE)
                ON CONFLICT (corp_client_id,yandex_uid,card_id)
                DO NOTHING
                RETURNING *
                """,
                (corp_client_id, yandex_uid, card_id),
            )
            return dict(cursor.fetchone())

    return wrapper


@pytest.fixture(name='select_employee_roles')
async def _select_employee_roles(pgsql):
    def wrapper(*, corp_client_id: str, yandex_uid: str):
        with pgsql['cargo_corp'].dict_cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM corp_clients.employee_roles
                WHERE corp_client_id = %s AND yandex_uid = %s
                """,
                (corp_client_id, yandex_uid),
            )

            return [dict(r) for r in cursor.fetchall()]

    return wrapper


@pytest.fixture(name='insert_role')
async def _insert_role(pgsql):
    def wrapper(
            *,
            role_name: str,
            permissions: List[str],
            corp_client_id: Optional[str] = None,
            is_removable: bool = True,
            role_id: Optional[str] = None,
    ):
        if role_id is None:
            role_id = str(uuid.uuid4())

        with pgsql['cargo_corp'].dict_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO corp_clients.client_roles
                (id,corp_client_id,role_name,permissions,is_removable,is_removed)
                VALUES(%s,%s,%s,%s,%s,FALSE)
                ON CONFLICT (corp_client_id,role_name)
                DO NOTHING
                RETURNING *
                """,
                (
                    role_id,
                    corp_client_id,
                    role_name,
                    permissions,
                    is_removable,
                ),
            )

            return cursor.fetchone()

    return wrapper


@pytest.fixture(name='insert_employee_role')
async def _insert_employee_role(pgsql):
    def wrapper(*, corp_client_id: str, yandex_uid: str, role_id: str):
        with pgsql['cargo_corp'].dict_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO corp_clients.employee_roles
                (corp_client_id,yandex_uid,role_id,is_removed)
                VALUES(%s,%s,%s,FALSE)
                RETURNING *
                """,
                (corp_client_id, yandex_uid, role_id),
            )

            return dict(cursor.fetchone())

    return wrapper
