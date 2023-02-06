from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/v3/state/targets_info/retrieve', self.handler_target_info,
        )

    async def handler_target_info(self, _):
        last_sync_date = '2021-06-03T11:22:41.836000+03:00'
        last_replicated = '2021-06-03T08:10:59.377000'
        return web.json_response(
            {
                'target_info': [
                    {
                        'target_name': 'processing_events',
                        'target_type': 'yt',
                        'replication_state': {'overall_status': 'enabled'},
                        'replication_settings': {
                            'replication_type': 'queue',
                            'iteration_field': {
                                'type': 'datetime',
                                'field': 'updated',
                            },
                        },
                        'yt_state': {
                            'full_path': '//some/path',
                            'clusters_states': [
                                {
                                    'cluster_name': 'arnold',
                                    'status': 'enabled',
                                    'last_sync_date': last_sync_date,
                                    'last_replicated': last_replicated,
                                },
                            ],
                        },
                    },
                ],
            },
        )
