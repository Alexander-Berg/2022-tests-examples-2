import datetime as dt
import json
import typing

from . import consts


def fetch_revision(
        pgsql: typing.Any,
        order_id: str = 'test_order',
        origin_revision_id: str = 'test_revision_id',
):
    cursor = pgsql['eats_order_revision'].cursor()
    cursor.execute(consts.REVISION_SELECT_SQL, [order_id, origin_revision_id])
    result = cursor.fetchone()

    if result is None:
        return {}

    (
        revision_id,
        order_id,
        origin_revision_id,
        cost_for_customer,
        document,
        is_applied,
        created_at,
    ) = result

    return {
        'id': revision_id,
        'order_id': order_id,
        'origin_revision_id': origin_revision_id,
        'cost_for_customer': cost_for_customer,
        'document': document,
        'is_applied': is_applied,
        'created_at': created_at,
    }


def insert_revision(
        pgsql: typing.Any,
        order_id: str = 'test_order',
        origin_revision_id: str = 'test_origin_revision_id',
        cost_for_customer: float = 100.500,
        document: typing.Any = None,
        is_applied: bool = True,
        created_at: dt.datetime = dt.datetime.now(),
        version: int = 1,
        service: str = 'eats_order_revision',
        initiator: str = 'system',
):
    cursor = pgsql['eats_order_revision'].cursor()
    cursor.execute(
        consts.REVISION_INSERT_SQL,
        [
            order_id,
            origin_revision_id,
            cost_for_customer,
            document,
            is_applied,
            created_at,
            version,
            service,
            initiator,
        ],
    )


def insert_tags(
        pgsql: typing.Any,
        revision_id: int,
        tags: list,
        created_at: dt.datetime = dt.datetime.now(),
):
    cursor = pgsql['eats_order_revision'].cursor()
    for tag in tags:
        cursor.execute(consts.TAGS_INSERT_SQL, [revision_id, tag, created_at])


def fetch_tags(pgsql: typing.Any, revision_id: int):
    cursor = pgsql['eats_order_revision'].cursor()
    cursor.execute(consts.TAGS_SELECT_SQL, [revision_id])
    return [i[0] for i in list(cursor)]


def fetch_revision_count(pgsql: typing.Any):
    cursor = pgsql['eats_order_revision'].cursor()
    cursor.execute(consts.REVISION_COUNT_SQL)
    result = cursor.fetchone()

    return result[0]


def fetch_revision_mixin_payload(
        pgsql: typing.Any, order_id: str, customer_service_id: str,
):
    cursor = pgsql['eats_order_revision'].cursor()
    cursor.execute(
        consts.REVISION_MIXIN_SELECT_SQL, [order_id, customer_service_id],
    )
    result = cursor.fetchone()

    return result[0]


def insert_revision_mixin(
        pgsql: typing.Any,
        order_id: str,
        customer_service_id: str,
        payload: typing.Any,
):
    cursor = pgsql['eats_order_revision'].cursor()
    cursor.execute(
        consts.REVISION_MIXIN_INSERT_SQL,
        [order_id, customer_service_id, payload],
    )


def insert_default_mixins(pgsql, load_json):
    mixins = load_json('mixins.json')

    insert_revision_mixin(
        pgsql, 'test_order', 'test_id_0', json.dumps(mixins['mixins'][0]),
    )
    insert_revision_mixin(
        pgsql, 'test_order', 'test_id_1', json.dumps(mixins['mixins'][1]),
    )
    insert_revision_mixin(
        pgsql, 'test_order', 'test_id_2', json.dumps(mixins['mixins'][1]),
    )


def fetch_mixins_count(pgsql: typing.Any):
    cursor = pgsql['eats_order_revision'].cursor()
    cursor.execute(consts.MIXINS_COUNT_SQL)
    result = cursor.fetchone()

    return result[0]
