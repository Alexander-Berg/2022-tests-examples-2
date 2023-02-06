def create_pipeline_sink_config(sink_name, bulk_size_threshold=100):
    # This is config from eventus admin for local tests
    return {
        'sink_name': sink_name,
        'arguments': {
            'bulk_size_threshold': bulk_size_threshold,
            'bulk_duration_of_data_collection_ms': 500,
            'input_queue_size': 10000,
            'output_queue_size': 1000,
        },
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


def create_rejects_pipeline(bulk_size_threshold=10):
    pipeline_sink_config = create_pipeline_sink_config(
        'bulk-rejects-redis-sink', bulk_size_threshold,
    )

    operation = {
        'name': 'accept-only-multioffer_reject-events',
        'operation_variant': {
            'operation_name': 'string_equal',
            'type': 'filter',
            'arguments': {'src': 'event', 'match_with': 'multioffer_reject'},
        },
    }

    admin_pipeline_config = [
        {
            'name': 'order-search-status-rejects',
            # default 3
            'number_of_threads': 1,
            'description': '',
            'st_ticket': '',
            'source': {'name': 'order-search-status-rejects'},
            'root': {
                'operations': [operation],
                'output': pipeline_sink_config,
            },
        },
    ]
    return admin_pipeline_config


def bid_pipeline():
    pipeline_sink_config = create_pipeline_sink_config('bulk-bids-redis-sink')

    operation = {
        'name': 'accept-only-multioffer_bid-events',
        'operation_variant': {
            'operation_name': 'string_array',
            'type': 'filter',
            'arguments': {
                'src': 'event',
                'policy': 'contains_any',
                'match_with': ['bid_created', 'bid_cancelled', 'bid_rejected'],
                'compare_policy': 'exact',
                'value_type': 'string',
            },
        },
    }

    admin_pipeline_config = [
        {
            'name': 'order-search-status-bids',
            # default 3
            'number_of_threads': 1,
            'description': '',
            'st_ticket': '',
            'source': {'name': 'order-search-status-bids'},
            'root': {
                'operations': [operation],
                'output': pipeline_sink_config,
            },
        },
    ]
    return admin_pipeline_config
