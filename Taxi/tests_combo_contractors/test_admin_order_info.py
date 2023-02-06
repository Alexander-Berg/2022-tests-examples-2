import pytest


@pytest.mark.parametrize(
    'test_order_id', ['order_id0', 'order_id1', 'order_id2'],
)
@pytest.mark.pgsql('combo_contractors', files=['batches.sql'])
async def test_get_batch_info_complete(
        taxi_combo_contractors, order_archive_mock, load_json, test_order_id,
):

    order_archive_mock.set_order_proc(
        [
            load_json('order_proc_0.json'),
            load_json('order_proc_1.json'),
            load_json('order_proc_2.json'),
        ],
    )

    response = await taxi_combo_contractors.post(
        '/v1/admin/order-info', json={'order_id': test_order_id},
    )

    assert response.json() == load_json('response_complete.json')


@pytest.mark.parametrize('test_order_id', ['order_id3', 'order_id4'])
@pytest.mark.pgsql('combo_contractors', files=['batches.sql'])
async def test_get_batch_info_transporting(
        taxi_combo_contractors, order_archive_mock, load_json, test_order_id,
):

    order_archive_mock.set_order_proc(
        [load_json('order_proc_3.json'), load_json('order_proc_4.json')],
    )

    response = await taxi_combo_contractors.post(
        '/v1/admin/order-info', json={'order_id': test_order_id},
    )

    assert response.json() == load_json('response_transporting.json')


@pytest.mark.parametrize('test_order_id', ['order_id5', 'order_id6'])
@pytest.mark.pgsql('combo_contractors', files=['batches.sql'])
async def test_get_batch_info_cancelled(
        taxi_combo_contractors, order_archive_mock, load_json, test_order_id,
):

    order_archive_mock.set_order_proc(
        [load_json('order_proc_5.json'), load_json('order_proc_6.json')],
    )

    response = await taxi_combo_contractors.post(
        '/v1/admin/order-info', json={'order_id': test_order_id},
    )

    assert response.json() == load_json('response_cancelled.json')
