import datetime
import json
import uuid

import pytest


def _gen_ids(count):
    return [str(uuid.uuid4()).replace('-', '') for _ in range(count)]


def _get_values_to_insert(values_groups):
    """
    Convert list of lists (or any iterables)
    into appropriate string for sql query.
    Example:
        Input:
            [['some str', 123], ['123', True]]
        Output:
            '('some str', 123), ('123', True)'
    """
    str_values_groups = []
    for values_group in values_groups:
        str_values_group = ','.join(
            map(
                lambda x: f'\'{x}\'' if isinstance(x, str) else f'{x}',
                values_group,
            ),
        )
        str_values_groups.append(f'({str_values_group})')
    return ','.join(str_values_groups)


@pytest.fixture(name='create_tickets')
async def _create_tickets(pgsql):
    def wrapper(
            count=None,
            ticket_ids=None,
            yandex_uid=None,
            phone_pd_id=None,
            corp_client_id=None,
            are_closed=True,
            are_successful=True,
    ):
        assert (count is not None) or (
            ticket_ids is not None
        ), 'must specify count or ids'
        assert not (
            (count is not None) and (ticket_ids is not None)
        ), 'must specify only ids or only count'

        if ticket_ids is None:
            custom_ids = _gen_ids(count)
            ticket_ids = custom_ids
        else:
            custom_ids = _gen_ids(len(ticket_ids))

        values_to_insert = [ticket_ids]
        for value in [
                yandex_uid,
                phone_pd_id,
                corp_client_id,
                are_closed,
                are_successful,
        ]:
            # add generated ids as field values if not specified
            if value is None:
                values_to_insert.append(custom_ids)
            else:
                values_to_insert.append([value] * len(ticket_ids))

        values_to_insert_str = _get_values_to_insert(zip(*values_to_insert))
        cursor = pgsql['cargo_crm'].cursor()
        cursor.execute(
            """
            INSERT INTO cargo_crm.tickets (
                ticket_id,
                yandex_uid,
                phone_pd_id,
                corp_client_id,
                is_closed,
                is_successful
            ) VALUES
                {}
            ON CONFLICT (ticket_id) DO NOTHING
            ;
            """.format(
                values_to_insert_str,
            ),
        )
        cursor.close()

    return wrapper


@pytest.fixture(name='find_stage_lock')
def _find_stage_lock(pgsql):
    def wrapper(ticket_id):
        cursor = pgsql['cargo_crm'].cursor()
        cursor.execute(
            """
            SELECT *
            FROM cargo_crm.stage_mutexes
            WHERE
                ticket_id = '{}'
            """.format(
                ticket_id,
            ),
        )
        row = cursor.fetchone()
        cursor.close()
        return row

    return wrapper


@pytest.fixture(name='acquire_stage_lock')
def _acquire_stage_lock(pgsql):
    def wrapper(ticket_id, created_at=None):
        cursor = pgsql['cargo_crm'].cursor()
        cursor.execute(
            """
            INSERT INTO cargo_crm.stage_mutexes (ticket_id, created_at)
            VALUES ('{0}', '{1}')
            ON CONFLICT (ticket_id) DO
            UPDATE SET
                created_at = '{1}'
            """.format(
                ticket_id,
                created_at or datetime.datetime.utcnow().isoformat(sep='T'),
            ),
        )
        cursor.close()

    return wrapper


@pytest.fixture(name='insert_ticket_data')
async def _insert_ticket_data(pgsql):
    def wrapper(
            *,
            ticket_id: str = None,
            manager_info_form: dict = None,
            company_info_form: dict = None,
            offer_info_form: dict = None,
            company_info_pd_form: dict = None,
            contract_traits_form: dict = None,
    ):
        if ticket_id is None:
            ticket_id = str(uuid.uuid4())

        ticket_data = {
            'manager_info_form': manager_info_form or {
                'manager': {'login': 'ya-manager'},
            },
            'company_info_form': company_info_form or {
                'name': 'Client',
                'country': 'rus',
            },
            'offer_info_form': offer_info_form or {'name': 'Client'},
            'company_info_pd_form': company_info_pd_form or {},
            'contract_traits_form': contract_traits_form or {
                'kind': 'offer',
                'type': 'prepaid',
            },
        }

        with pgsql['cargo_crm'].dict_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cargo_crm_manager.tickets_data
                (ticket_id, ticket_data)
                VALUES (%s,%s)
                RETURNING ticket_id
                """,
                (ticket_id, json.dumps(ticket_data)),
            )

            return dict(cursor.fetchone())

    return wrapper
