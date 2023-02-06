from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink
from nile.api.v1 import Record

from projects.common.nile import test_utils
from projects.customer_care.nirvana import candidates_for_communication


def iter_records(data):
    for elem in data:
        params = {k: test_utils.to_bytes(v) for k, v in elem.items()}
        yield Record(**params)


def test_candidates_selection(load_json):
    job = clusters.MockCluster().job()

    chats_table = job.table('//chats').label('chats_table')
    orders_table = job.table('//orders').label('orders_table')
    chatterbox_table = job.table('//chatterbox').label('chatterbox_table')
    candidates_for_communication.join_tables(
        chats_table, orders_table, chatterbox_table,
    ).label('output')

    chats_records = list(iter_records(load_json('chats.json')))
    orders_records = list(iter_records(load_json('orders.json')))
    chatterbox_records = list(iter_records(load_json('chatterbox.json')))

    output = []
    job.local_run(
        sources={
            'chats_table': StreamSource(chats_records),
            'orders_table': StreamSource(orders_records),
            'chatterbox_table': StreamSource(chatterbox_records),
        },
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 4

    assert output[0].order_id == b'2818adb2db8a2d208725844de7a101e1'
    assert output[0].user_id_orders == b'4e27ed23e5aeb185f84804b8d764a1ab'
    assert output[0].user_id_chatterbox == b'4e27ed23e5aeb185f84804b8d764a1ab'
    assert output[0].did_user_contact_support
    assert output[0].customer_care_reason == 'nope'

    assert output[1].order_id == b'5ba55065fb403669a4d4256d859c690b'
    assert output[1].user_id_orders == b'607bb778179b48d3c0e9295fe87f8dc9'
    assert output[1].user_id_chatterbox is None
    assert not output[1].did_user_contact_support
    assert output[1].customer_care_reason == 'cancel'
    assert not output[1].paid_cancel_flg

    assert output[2].order_id == b'817c9af0d9a120cebd2f9bcb0ae22f1e'
    assert output[2].user_id_orders == b'd53df4077c903d33a99ad820beac9c82'
    assert output[2].user_id_chatterbox is None
    assert not output[2].did_user_contact_support
    assert output[2].customer_care_reason == 'nope'

    assert output[3].order_id == b'af29439147fd3422a75c90e0baecee15'
    assert output[3].user_id_orders == b'33a34dded1ac96cc404bf31fae51c3c3'
    assert output[3].user_id_chatterbox is None
    assert not output[3].did_user_contact_support
    assert output[3].status == b'cancelled'
    assert output[3].customer_care_reason == 'cancel'
    assert output[3].paid_cancel_flg
