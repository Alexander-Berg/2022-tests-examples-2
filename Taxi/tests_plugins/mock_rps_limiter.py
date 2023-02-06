import asyncio
import collections

import pytest


@pytest.fixture(name='rps_limiter', autouse=True)
def _rps_limiter(mockserver):
    class RateLimiterContext:
        def __init__(self):
            self.budgets = {}
            self.is_down = False
            self.fail_attempts = 0
            # incoming requests
            self.requested = collections.defaultdict(list)
            self.resources = set()

        def set_budget(self, resource, budget):
            self.budgets[resource] = budget
            self.resources.add(resource)

        @property
        def call_count(self):
            return _rps_quotas.times_called

        async def wait_request(self, service, resources):
            for _ in range(100):
                if self._find_and_compare_request(
                        resources, self.requested[service],
                ):
                    break
                # do not use wait_call(), because it destroys event in the
                # queue and following times_called function returns wrong
                # value
                await asyncio.sleep(0.1)

        def _find_and_compare_request(self, resources, received):
            keys = set()
            for resource in resources:
                keys.add(resource)

            for received_request in received:
                if keys == received_request.keys():
                    self._compare(resources, received_request)
                    received.remove(received_request)
                    return True

            return False

        def _compare(self, resources, received):
            if isinstance(resources, (set, list, tuple)):
                # nothing more to compare, resource name already matched
                return
            if isinstance(resources, dict):
                for resource, properties in resources.items():
                    for name, value in properties.items():
                        if received[resource].get(name) != value:
                            raise RuntimeError(
                                'Incoming request %s mismatch received one %s'
                                % (properties, received[resource]),
                            )
            else:
                raise RuntimeError(
                    'Wrong resources type: %s' % type(resources),
                )

    context = RateLimiterContext()

    @mockserver.json_handler('/statistics/v1/rps-quotas')
    def _rps_quotas(request):
        service = request.args['service']
        requests = request.json['requests']
        request = {
            req['resource']: req
            for req in requests
            if req['resource'] in context.resources
        }
        context.requested[service].append(request)
        if context.is_down:
            return mockserver.make_response(status=500)
        if context.fail_attempts > 0:
            context.fail_attempts -= 1
            return mockserver.make_response(status=500)
        quotas = []
        for quota_request in requests:
            resource = quota_request['resource']
            requested = quota_request['requested-quota']
            quota = 0
            if resource in context.budgets:
                quota = min(context.budgets[resource], requested)
                context.budgets[resource] -= quota
            quotas.append({'resource': resource, 'assigned-quota': quota})
        return {'quotas': quotas}

    return context
