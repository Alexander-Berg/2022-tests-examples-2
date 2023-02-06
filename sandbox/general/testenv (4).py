import logging
import re
from collections import defaultdict, OrderedDict

from sandbox.projects.common.testenv_client import TEClient
from sandbox.projects.yabs.qa.utils.resource import get_resource_attributes


logger = logging.getLogger(__name__)


def get_service_tag_from_testenv_resource_info(testenv_resource_info):
    resource_attributes = get_resource_attributes(testenv_resource_info["resource_id"])
    try:
        return resource_attributes["service_tag"]
    except KeyError:
        logger.warning("Resource %d has no attribute 'service_tag'", testenv_resource_info['resource_id'])
        return None


def get_testenv_hamster_endpoints(testenv_resources, ignore_statuses=('BAD',), ok_old_resources_to_keep=None):
    """Get hamster endpoint resources from testenv

    :param testenv_resources: Testenv resources info
    :type testenv_resources: list[dict]
    :param ignore_statuses: Ignore resource with statuses, defaults to ('BAD',)
    :type ignore_statuses: tuple, optional
    :param ok_old_resources_to_keep: List of service tag for which to keep OK_OLD resources, defaults to None
    :type ok_old_resources_to_keep: list[str], optional
    :return: Mapping from service tag to list of resource ids
    :rtype: dict[str, list]
    """
    hamster_endpoint_resource_name_re = re.compile(r'^YABS_SERVER_([A-Z_]+)_ENDPOINT$')
    ok_old_resources_to_keep = ok_old_resources_to_keep or []

    endpoint_resources = defaultdict(OrderedDict)
    for testenv_resource in testenv_resources:
        if not hamster_endpoint_resource_name_re.match(testenv_resource['name']):
            logger.debug(
                "Ignoring resource %s because its name %s does not match pattern %s",
                testenv_resource['resource_id'],
                testenv_resource['name'],
                hamster_endpoint_resource_name_re.pattern,
            )
            continue

        resource_status = testenv_resource['status']
        if resource_status in ignore_statuses:
            logger.debug("Ignoring resource %s with status %s", testenv_resource['resource_id'], resource_status)
            continue

        service_tag = get_service_tag_from_testenv_resource_info(testenv_resource)
        if not service_tag:
            logger.debug("Failed to get service tag from resource %s", testenv_resource["resource_id"])
            continue

        if resource_status == 'OK_OLD' and service_tag not in ok_old_resources_to_keep:
            continue

        endpoint_resources[service_tag].setdefault(resource_status, []).append(testenv_resource)

    active_endpoint_resources = defaultdict(list)
    for service_tag, filtered_service_endpoint_resources in endpoint_resources.items():
        for status, resources in filtered_service_endpoint_resources.items():
            resource = max(resources, key=lambda x: x['resource_timestamp'])
            logger.debug('Found active %s %s, resource_id=%s', status, resource['name'], resource['resource_id'])
            active_endpoint_resources[service_tag].append(resource['resource_id'])

    return dict(active_endpoint_resources)


def get_ok_testenv_hamster_endpoints():
    """Get ok (OK, SWITCHING) hamster resources from testenv

    :return: Mapping from service tag to list of resource ids
    :rtype: dict[str, list]
    """
    from retrying import retry

    get_testenv_resources = retry(stop_max_attempt_number=10)(TEClient.get_resources)
    testenv_resources = get_testenv_resources('yabs-2.0')
    ignore_testenv_resource_statuses={'BAD', 'OK_OLD', 'CHECKING', 'NOT_CHECKED'}
    endpoints = get_testenv_hamster_endpoints(
        testenv_resources,
        ignore_statuses=ignore_testenv_resource_statuses
    )
    return endpoints
