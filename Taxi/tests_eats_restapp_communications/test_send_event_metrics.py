import pytest


def get_actual_nonempty_metrics(metrics_before_test, metrics_after_test):
    actual_metrics = {}
    for metric in metrics_after_test.keys():
        if metric in metrics_before_test.keys():
            if metrics_after_test[metric] - metrics_before_test[metric] != 0:
                actual_metrics[metric] = (
                    metrics_after_test[metric] - metrics_before_test[metric]
                )
        else:
            actual_metrics[metric] = metrics_after_test[metric]
    return actual_metrics


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_bind_places_logins.sql',),
)
@pytest.mark.parametrize(
    'event_type, slug, expected_metrics',
    [
        pytest.param(
            'password-request-reset',
            '8Y2IS654-4J2',
            {
                'method-types-metrics': {'emails': 3},
                'event-types-metrics': {'password-request-reset': 3},
            },
        ),
        pytest.param(
            'place-onboarding-launch',
            'KHGZM4C4-QTH1',
            {
                'method-types-metrics': {'emails': 3},
                'event-types-metrics': {'place-onboarding-launch': 3},
            },
        ),
        pytest.param(
            'eats-partners-generate-credentials',
            'SVB507E4-OYX1',
            {
                'method-types-metrics': {'emails': 3},
                'event-types-metrics': {
                    'eats-partners-generate-credentials': 3,
                },
            },
        ),
        pytest.param(
            'daily-digests',
            '',
            {
                'method-types-metrics': {'telegram': 5},
                'event-types-metrics': {'daily-digests': 5},
            },
        ),
        pytest.param(
            'cancelled-tg-alert',
            '',
            {
                'method-types-metrics': {'telegram': 5},
                'event-types-metrics': {'cancelled-tg-alert': 5},
            },
        ),
    ],
)
async def test_email_metrics(
        stq_runner,
        taxi_eats_restapp_communications_monitor,
        mockserver,
        mock_core_places,
        mock_personal_telegram_retrieve,
        mock_catalog_storage,
        event_type,
        slug,
        expected_metrics,
):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/' + slug + '/send',
    )
    def _mock_send_event(request):
        if request.json['to'][0]['email'] == 'email2':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [2],
                'places': ['place2 (address2)'],
            }
        elif request.json['to'][0]['email'] == 'common_email':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [1],
                'places': ['place1 (address1)'],
            }
        elif request.json['to'][0]['email'] == 'other_email':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [1, 4],
                'places': ['place1 (address1)', 'place4 (address4)'],
            }
        else:
            assert request.json == ''
        return mockserver.make_response(
            status=200,
            json={
                'result': {'status': 'ok', 'task_id': '1', 'message_id': '1'},
            },
        )

    method_types_metrics_bfr_test = (
        await taxi_eats_restapp_communications_monitor.get_metric(
            'method-types-metrics',
        )
    )
    event_types_metrics_bfr_test = (
        await taxi_eats_restapp_communications_monitor.get_metric(
            'event-types-metrics',
        )
    )

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id=f'fake_task-{event_type}',
    )

    method_types_metrics_aft_test = (
        await taxi_eats_restapp_communications_monitor.get_metric(
            'method-types-metrics',
        )
    )
    event_types_metrics_aft_test = (
        await taxi_eats_restapp_communications_monitor.get_metric(
            'event-types-metrics',
        )
    )

    actual_method_types_metrics = get_actual_nonempty_metrics(
        method_types_metrics_bfr_test, method_types_metrics_aft_test,
    )
    actual_event_types_metrics = get_actual_nonempty_metrics(
        event_types_metrics_bfr_test, event_types_metrics_aft_test,
    )

    assert (
        actual_method_types_metrics == expected_metrics['method-types-metrics']
    )
    assert (
        actual_event_types_metrics == expected_metrics['event-types-metrics']
    )
