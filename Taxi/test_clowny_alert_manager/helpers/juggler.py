import copy
import operator


def _make_param_getter(*names):
    return operator.itemgetter(*(f'{x}_name' for x in names))


def apply_filters(data: dict, params: dict, ignore_filters=False):
    with_children = params.get('include_children')
    with_meta = params.get('include_meta')
    with_notifications = params.get('include_notifications')

    tag_name = params.get('tag_name') if not ignore_filters else None
    ns_name = params.get('namespace_name') if not ignore_filters else None
    if {'host_name', 'service_name'} < params.keys():
        host_srv_names = (
            _make_param_getter('host', 'service')(params)
            if not ignore_filters
            else None
        )
    else:
        host_srv_names = None

    result: dict = {}

    for host, host_services in data.items():
        for service_name, service in host_services.items():
            if tag_name and tag_name not in service.get('tags', []):
                continue
            if (
                    ns_name
                    and service.get('namespace')
                    and ns_name != service['namespace']
            ):
                continue
            if host_srv_names:
                if (host, service_name) != host_srv_names:
                    continue

            service = copy.deepcopy(service)
            if not with_children:
                service.pop('children', None)
            if not with_meta:
                service.pop('meta', None)
            if not with_notifications:
                service.pop('notifications', None)
            result.setdefault(host, {})[service_name] = service
    return result
