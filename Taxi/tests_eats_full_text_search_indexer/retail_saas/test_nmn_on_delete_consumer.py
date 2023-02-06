import json

import pytest

LB_TOPIC = 'eda/test/eda-test-eats-nomenclature-on-delete-active-assortment'
LB_CONSUMER = 'nomenclature_on_delete_active_assortment'


def enable_consumer(should_enable_consumer: bool):
    return pytest.mark.config(
        EATS_FULL_TEXT_SEARCH_INDEXER_NOMENCLATURE_SETTINGS={
            'enable_nmn_on_delete_assortment_consumer': should_enable_consumer,
        },
    )


@pytest.mark.parametrize(
    'should_enable_consumer',
    (
        pytest.param(True, marks=enable_consumer(True), id='Enable consumer'),
        pytest.param(
            False, marks=enable_consumer(False), id='Disable consumer',
        ),
    ),
)
async def test_enable_consumer(
        taxi_eats_full_text_search_indexer,
        stq,
        testpoint,
        # parametrize
        should_enable_consumer,
):
    """
    Проверяем, что если консьюмер включен, то при чтении сообщения
    ставится stq таска в очередь удаления плейса
    """

    @testpoint('logbroker_commit')
    def commit(cookie):
        pass

    place_id = '1'
    message = {
        'place_id': place_id,
        'timestamp': '2021-03-04T00:00:00',
        'timestamp_raw': '2021-03-04T17:19:42.838992671+03:00',
    }
    await push_lb_message(
        taxi_eats_full_text_search_indexer, json.dumps(message),
    )

    if should_enable_consumer:
        await commit.wait_call()
        assert stq.eats_full_text_search_indexer_delete_retail_place.has_calls
        task_info = (
            stq.eats_full_text_search_indexer_delete_retail_place.next_call()
        )
        assert task_info['kwargs']['place_id'] == place_id
    else:
        assert not commit.has_calls
        assert (
            not stq.eats_full_text_search_indexer_delete_retail_place.has_calls
        )


@enable_consumer(should_enable_consumer=True)
async def test_split_message(
        taxi_eats_full_text_search_indexer, stq, testpoint, stq_runner,
):
    """
    Проверяем, что если несколько сообщений склеились в одно, то
    stq таска ставится на каждое из этих сообщений
    """

    @testpoint('logbroker_commit')
    def commit(cookie):
        pass

    place_ids = {'1', '2', '3'}
    message = {
        'timestamp_raw': '2021-03-04T17:19:42.838992671+03:00',
        'place_id': '1',
        'timestamp': '2021-03-04T00:00:00',
    }
    full_message = ''
    for place_id in place_ids:
        message['place_id'] = place_id
        full_message += json.dumps(message) + '\n'

    await push_lb_message(taxi_eats_full_text_search_indexer, full_message)

    await commit.wait_call()

    assert (
        stq.eats_full_text_search_indexer_delete_retail_place.times_called
        == len(place_ids)
    )
    stq_place_ids = set()
    for _ in range(len(place_ids)):
        task_info = (
            stq.eats_full_text_search_indexer_delete_retail_place.next_call()
        )
        stq_place_ids.add(task_info['kwargs']['place_id'])
        await stq_runner.eats_full_text_search_indexer_delete_retail_place.call(  # noqa: E501 pylint: disable=line-too-long
            task_id=task_info['id'], kwargs=task_info['kwargs'],
        )

    assert stq_place_ids == place_ids


async def push_lb_message(taxi_eats_full_text_search_indexer, data):
    response = await taxi_eats_full_text_search_indexer.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': LB_CONSUMER,
                'data': data,
                'topic': LB_TOPIC,
                'cookie': 'some_cookie',
            },
        ),
    )
    assert response.status_code == 200
