import pytest

from taxi import discovery

from taxi_billing_calculators.stq.driver_mode_subscription import task


@pytest.mark.parametrize(
    'test_data_path, expected_finished_docs_ids, expected_stq_tasks',
    [
        (
            'multiple_open_subscriptions.json',
            [496, 28],
            [
                ('8128_0', {'log_extra': {}, 'subscription_doc_id': 8128}),
                (
                    '496_8128',
                    {
                        'log_extra': {},
                        'subscription_doc_id': 496,
                        'subscription_end': '2018-05-09T20:00:00.000000+00:00',
                    },
                ),
            ],
        ),
        (
            'one_open_subscription.json',
            [6],
            [
                ('28_0', {'log_extra': {}, 'subscription_doc_id': 28}),
                (
                    '6_28',
                    {
                        'log_extra': {},
                        'subscription_doc_id': 6,
                        'subscription_end': '2018-05-09T20:00:00.000000+00:00',
                    },
                ),
            ],
        ),
        (
            'no_subscriptions.json',
            [],
            [('6_0', {'log_extra': {}, 'subscription_doc_id': 6})],
        ),
        (
            'no_open_subscriptions.json',
            [],
            [
                ('28_0', {'log_extra': {}, 'subscription_doc_id': 28}),
                (
                    '6_28',
                    {
                        'log_extra': {},
                        'subscription_doc_id': 6,
                        'subscription_end': '2018-05-09T20:00:00.000000+00:00',
                    },
                ),
            ],
        ),
        (
            'event_at_in_the_past.json',
            [28],
            [
                (
                    '28_6',
                    {
                        'log_extra': {},
                        'subscription_doc_id': 28,
                        'subscription_end': '2018-05-09T20:00:00.000000+00:00',
                    },
                ),
            ],
        ),
    ],
)
# pylint: disable=invalid-name
async def test_calculators_driver_mode_subscription(
        test_data_path,
        expected_finished_docs_ids,
        expected_stq_tasks,
        *,
        patch,
        load_json,
        patch_aiohttp_session,
        request_headers,
        response_mock,
        taxi_billing_calculators_stq_driver_mode_subscription_ctx,
):
    data = load_json(test_data_path)
    actual_finished_docs_ids = []

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'v1/docs/search' in url:
            docs = (
                [data['request']]
                if 'doc_id' in json
                else data['search_response_docs'] + [data['request']]
            )
            return response_mock(json={'docs': docs})
        if 'v1/docs/finish_processing' in url:
            actual_finished_docs_ids.append(json['doc_id'])
            return response_mock(json={'finished': True, 'status': 'complete'})
        raise NotImplementedError

    stq_tasks = []

    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def _stq_client_put(
            queue, eta=None, task_id=None, args=None, kwargs=None,
    ):
        stq_tasks.append((task_id, kwargs))

    await task.process_doc(
        taxi_billing_calculators_stq_driver_mode_subscription_ctx,
        doc_id=data['request']['doc_id'],
        kind=data['request']['kind'],
    )

    assert stq_tasks == expected_stq_tasks
    assert sorted(actual_finished_docs_ids) == sorted(
        expected_finished_docs_ids,
    )
