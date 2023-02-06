class WorkerTestpointWithMetrics:
    def __init__(
            self, testpoint, taxi_segments_provider_monitor, worker_name: str,
    ):
        self.metrics = None

        @testpoint(f'{worker_name}-finished')
        async def worker_finished(data):
            self.metrics = await taxi_segments_provider_monitor.get_metric(
                f'{worker_name}',
            )

        self.worker_finished = worker_finished
