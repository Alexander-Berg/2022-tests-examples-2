def create_pipelines(bulk_size_threshold=10):
    # This is config from eventus admin for local tests
    pipeline_sink_config = {
        'sink_name': 'events-sink',
        'arguments': {},
        # example of retry config, can be empty, if retries not needed
        'error_handling_policy': {
            'retry_policy': {
                'attempts': 1,
                'min_delay_ms': 1,
                'max_delay_ms': 1,
                'delay_factor': 1,
            },
            'erroneous_statistics_level': 'error',
        },
    }

    admin_pipeline_config = [
        {
            'name': 'eventus-subventions-tags',
            # default 3
            'number_of_threads': 1,
            'description': '',
            'st_ticket': '',
            'source': {'name': 'tags-events-subventions'},
            'root': {
                'operations': [
                    {
                        'name': 'extract-driver-profile-id',
                        'operation_variant': {
                            'operation_name': 'set_key_flat',
                            'type': 'mapper',
                            'arguments': {
                                'flat_key': 'driver_profile_id',
                                'recursive_keys': ['profile_id'],
                            },
                        },
                    },
                    {
                        'name': 'set-event-type',
                        'operation_variant': {
                            'operation_name': 'set_string_value',
                            'type': 'mapper',
                            'arguments': {'value': 'tags', 'dst_key': 'type'},
                        },
                    },
                    {
                        'name': 'log',
                        'operation_variant': {
                            'operation_name': 'log_event',
                            'type': 'mapper',
                            'arguments': {
                                'marker': 'subventions-tags event: ',
                                'log_level': 'info',
                            },
                        },
                    },
                ],
                'output': pipeline_sink_config,
            },
        },
        {
            'name': 'eventus-geohierarchies',
            # default 3
            'number_of_threads': 1,
            'description': '',
            'st_ticket': '',
            'source': {'name': 'contractor-geo-hierarchies'},
            'root': {
                'operations': [
                    {
                        'name': 'extract-driver-profile-id',
                        'operation_variant': {
                            'operation_name': 'set_key_flat',
                            'type': 'mapper',
                            'arguments': {
                                'flat_key': 'driver_profile_id',
                                'recursive_keys': ['driver_id'],
                            },
                        },
                    },
                    {
                        'name': 'set-event-type',
                        'operation_variant': {
                            'operation_name': 'set_string_value',
                            'type': 'mapper',
                            'arguments': {'value': 'zone', 'dst_key': 'type'},
                        },
                    },
                    {
                        'name': 'log',
                        'operation_variant': {
                            'operation_name': 'log_event',
                            'type': 'mapper',
                            'arguments': {
                                'marker': 'geohierarchy event: ',
                                'log_level': 'info',
                            },
                        },
                    },
                ],
                'output': pipeline_sink_config,
            },
        },
    ]
    return admin_pipeline_config
