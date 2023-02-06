def test_server_log(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['server-log'] = {
        'send-to-yt': True,
    }
    default_repository['services/test-service/yt-uploads/server_log.yaml'] = {
        'data_format': 'dsv',
        'timestamp_format': 'legacy-local-without-tz',
        'push-client-override': {'streams': 5},
        'logfeller': {'lifetimes': {'1d': '2d', '1h': '1d'}},
        'logrotate': False,
        'table_meta': {
            'attributes': {
                'schema': [
                    {'name': 'level', 'type': 'string'},
                    {'name': 'link', 'type': 'string'},
                    {'name': 'text', 'type': 'string'},
                    {'name': 'trace_id', 'type': 'string'},
                    {'name': 'span_id', 'type': 'string'},
                    {'name': 'parent_id', 'type': 'string'},
                    {'name': 'parent_link', 'type': 'string'},
                    {'name': 'stopwatch_name', 'type': 'string'},
                    {'name': 'total_time', 'type': 'string'},
                ],
            },
        },
    }
    generate_services_and_libraries(
        default_repository, 'test_server_log/test', default_base,
    )
