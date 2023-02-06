import pytest


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.translations(
        clownductor={
            'alert_manager.virtual_meta_watchdog.downtime_description': {
                'ru': (
                    'Хост может быть недоступен, однако по данным yp '
                    'ситуация штатная, и он скоро поднимется.'
                ),
            },
        },
    ),
]


@pytest.mark.now('2022-07-07T14:02:00+0300')
async def test_simple(
        cron_runner, mockserver, load_json, mock_juggler_api, mock_clownductor,
):
    @mock_juggler_api('/v2/events/get_raw_events')
    def _mock_get_raw_events(request):
        assert request.json == load_json(
            'expected_raw_events_request_simple.json',
        )

        return load_json('juggler_events_simple.json')

    @mock_clownductor('/v1/hosts/')
    def _mock_hosts(request):
        fqdn = request.query['fqdn']
        data = load_json('clownductor_hosts_simple.json')
        if fqdn not in data:
            return []

        return [data[fqdn]]

    @mock_clownductor('/v1/services/')
    def _mock_services(request):
        data = load_json('clownductor_services_simple.json')
        service_id = request.query['service_id']

        return [data[service_id]]

    @mockserver.json_handler('/yp-api/ObjectService/SelectObjects')
    def _mock_select_objects(request):
        assert request.json['object_type'] == 'pod'
        assert request.json['filter'] == {
            'query': (
                '[/status/maintenance/state] = "acknowledged" or '
                '[/status/maintenance/state] = "in_progress"'
            ),
        }
        assert request.json['selector'] == {
            'paths': ['/status/dns/persistent_fqdn'],
        }

        location = ['sas', 'vla', 'man', 'iva', 'myt'][
            _mock_select_objects.times_called
        ]
        data = load_json('host_maintenance_status_simple.json')

        return {
            'results': [{'values': [fqdn]} for fqdn in data.get(location, [])],
            'timestamp': 228,
        }

    @mock_juggler_api('/v2/downtimes/get_downtimes')
    def _mock_get_downtimes(request):
        if request.json.get('page') == 2:
            return {'items': [], 'page': 2}

        assert request.json == {
            'exclude_future': True,
            'include_expired': False,
            'include_warnings': False,
            'page_size': 100,
            'sort_by': 'ID',
            'sort_order': 'DESC',
            'filters': [
                {
                    'source': (
                        'clowny-alert-manager.virtual_meta_watchdog.testing'
                    ),
                },
            ],
        }

        return load_json('juggler_downtimes_simple.json')

    @mock_juggler_api('/v2/downtimes/set_downtimes')
    def _mock_set_downtimes(request):
        assert request.headers['Authorization'] == 'OAuth juggler_oauth'

        data = load_json('expected_set_downtimes_simple.json')
        downtime_id = request.json.get('downtime_id') or ''

        assert request.json == data[downtime_id]

        return {'downtime_id': '228'}

    await cron_runner.virtual_meta_watchdog()

    assert _mock_get_raw_events.times_called == 1
    assert _mock_hosts.times_called == 4
    assert _mock_services.times_called == 3
    assert _mock_select_objects.times_called == 5
    assert _mock_get_downtimes.times_called == 2
    assert _mock_set_downtimes.times_called == 2
