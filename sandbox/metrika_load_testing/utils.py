import time

import infra.yp_service_discovery.python.resolver.resolver as yp_sd_resolver
import infra.yp_service_discovery.api.api_pb2 as yp_sd_api


def resolve_endpoints(endpoint_set_id, datacenter):
    resolver = yp_sd_resolver.Resolver(client_name='metrika-load-testing')

    request = yp_sd_api.TReqResolveEndpoints()
    request.cluster_name = datacenter
    request.endpoint_set_id = endpoint_set_id

    result = resolver.resolve_endpoints(request)
    return result.endpoint_set.endpoints


def get_tank_address(
    endpoint_set_id,
    datacenter,
    timeout=600,
    poll_period=15,
):

    host = None
    port = None

    start_ts = time.time()
    current_ts = time.time()

    while True:
        if (current_ts - start_ts) > timeout:
            raise ValueError('Failed to resolve tank endpoints: timeout reached ({}s)'.format(timeout))

        endpoints = resolve_endpoints(endpoint_set_id, datacenter)
        if endpoints:
            host = endpoints[0].fqdn
            port = endpoints[0].port
            break

        time.sleep(poll_period)
        current_ts = time.time()

    return host, port
