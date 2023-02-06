# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
from api_proxy_plugins import *  # noqa: F403 F401
import pytest

from tests_api_proxy.api_proxy.utils import admin as utils_admin
from tests_api_proxy.api_proxy.utils import endpoints as utils_endpoints
from tests_api_proxy.api_proxy.utils import resources as utils_resources


class Resources:
    Failure = utils_resources.Failure

    def __init__(self, taxi_api_proxy, testpoint):
        self._api_proxy = taxi_api_proxy
        self._testpoint = testpoint

    async def fetch_current_stable(self, resource_id):
        return await utils_resources.fetch_current_stable(
            self._api_proxy, resource_id,
        )

    async def fetch_current_prestable(self, resource_id):
        return await utils_resources.fetch_current_prestable(
            self._api_proxy, resource_id,
        )

    async def put_resource(self, params, json, prestable=False):
        return await utils_resources.put_resource(
            self._api_proxy,
            self._testpoint,
            params=params,
            json=json,
            prestable=prestable,
        )

    async def delete_resource(self, params):
        return await utils_resources.delete_resource(
            self._api_proxy, self._testpoint, params=params,
        )

    async def downgrade_resource(self, params, expected_new=None):
        return await utils_resources.downgrade_resource(
            self._api_proxy,
            self._testpoint,
            params=params,
            expected_new=expected_new,
        )

    async def release_prestable_resource(self, params, no_check=False):
        return await utils_resources.release_prestable_resource(
            self._api_proxy, self._testpoint, params=params, no_check=no_check,
        )

    async def delete_prestable_resource(self, params, no_check=False):
        return await utils_resources.delete_prestable_resource(
            self._api_proxy, self._testpoint, params=params, no_check=no_check,
        )

    async def safely_create_resource(
            self,
            resource_id,
            url,
            method,
            dev_team=None,
            duty_group_id=None,
            duty_abc=None,
            summary=None,
            tvm_name=None,
            qos_taxi_config=None,
            timeout=None,
            timeout_taxi_config=None,
            max_retries=None,
            max_retries_taxi_config=None,
            prestable=None,
            caching_enabled=False,
            rps_limit=None,
            use_envoy=False,
    ):
        return await utils_admin.create_resource(
            self._api_proxy,
            self._testpoint,
            resource_id=resource_id,
            url=url,
            method=method,
            dev_team=dev_team,
            duty_group_id=duty_group_id,
            duty_abc=duty_abc,
            summary=summary,
            tvm_name=tvm_name,
            qos_taxi_config=qos_taxi_config,
            timeout=timeout,
            timeout_taxi_config=timeout_taxi_config,
            max_retries=max_retries,
            max_retries_taxi_config=max_retries_taxi_config,
            prestable=prestable,
            caching_enabled=caching_enabled,
            rps_limit=rps_limit,
            use_envoy=use_envoy,
        )

    async def safely_update_resource(
            self,
            resource_id,
            url,
            method,
            dev_team=None,
            duty_group_id=None,
            duty_abc=None,
            summary=None,
            tvm_name=None,
            timeout=None,
            timeout_taxi_config=None,
            max_retries=None,
            max_retries_taxi_config=None,
            prestable=None,
            caching_enabled=False,
            rps_limit=None,
    ):
        return await utils_admin.update_resource(
            self._api_proxy,
            self._testpoint,
            resource_id=resource_id,
            url=url,
            method=method,
            dev_team=dev_team,
            duty_group_id=duty_group_id,
            duty_abc=duty_abc,
            summary=summary,
            tvm_name=tvm_name,
            timeout=timeout,
            timeout_taxi_config=timeout_taxi_config,
            max_retries=max_retries,
            max_retries_taxi_config=max_retries_taxi_config,
            prestable=prestable,
            caching_enabled=caching_enabled,
            rps_limit=rps_limit,
        )

    async def safely_delete_resource(self, resource_id):
        return await utils_admin.delete_resource(
            self._api_proxy, self._testpoint, resource_id,
        )

    async def finalize_resource_prestable(
            self,
            resource_id,
            resolution,
            force_prestable_revision=None,
            force_recall=1,
    ):
        return await utils_admin.finalize_resource_prestable(
            self._api_proxy,
            self._testpoint,
            resource_id=resource_id,
            resolution=resolution,
            force_prestable_revision=force_prestable_revision,
            force_recall=force_recall,
        )


@pytest.fixture(name='resources')
def _resources_fixture(taxi_api_proxy, testpoint):
    return Resources(taxi_api_proxy, testpoint)


class Endpoints:
    Failure = utils_endpoints.Failure

    def __init__(self, taxi_api_proxy, testpoint):
        self._api_proxy = taxi_api_proxy
        self._testpoint = testpoint

    async def fetch_current_stable(self, endpoint_id):
        return await utils_endpoints.fetch_current_stable(
            self._api_proxy, endpoint_id,
        )

    async def fetch_current_prestable(self, endpoint_id):
        return await utils_endpoints.fetch_current_prestable(
            self._api_proxy, endpoint_id,
        )

    async def put_endpoint(
            self, params, json, prestable=False, check_draft=True,
    ):
        return await utils_endpoints.put_endpoint(
            self._api_proxy,
            self._testpoint,
            params=params,
            json=json,
            prestable=prestable,
            check_draft=check_draft,
        )

    async def delete_endpoint(self, params):
        return await utils_endpoints.delete_endpoint(
            self._api_proxy, self._testpoint, params=params,
        )

    async def downgrade_endpoint(self, params, expected_new=None):
        return await utils_endpoints.downgrade_endpoint(
            self._api_proxy,
            self._testpoint,
            params=params,
            expected_new=expected_new,
        )

    async def release_prestable_endpoint(self, params, no_check=False):
        return await utils_endpoints.release_prestable_endpoint(
            self._api_proxy, self._testpoint, params=params, no_check=no_check,
        )

    async def delete_prestable_endpoint(self, params, no_check=False):
        return await utils_endpoints.delete_prestable_endpoint(
            self._api_proxy, self._testpoint, params=params, no_check=no_check,
        )

    async def safely_create_endpoint(
            self,
            path,
            endpoint_id=None,
            dev_team=None,
            duty_group_id=None,
            duty_abc=None,
            put_handler=None,
            post_handler=None,
            get_handler=None,
            patch_handler=None,
            delete_handler=None,
            prestable=None,
            tests=None,
            check_draft=True,
            enabled=True,
    ):
        return await utils_admin.create_endpoint(
            self._api_proxy,
            self._testpoint,
            path=path,
            endpoint_id=endpoint_id,
            dev_team=dev_team,
            duty_group_id=duty_group_id,
            duty_abc=duty_abc,
            put_handler=put_handler,
            post_handler=post_handler,
            get_handler=get_handler,
            patch_handler=patch_handler,
            delete_handler=delete_handler,
            prestable=prestable,
            tests=tests,
            check_draft=check_draft,
            enabled=enabled,
        )

    async def safely_update_endpoint(
            self,
            path,
            endpoint_id=None,
            dev_team=None,
            duty_group_id=None,
            duty_abc=None,
            put_handler=None,
            post_handler=None,
            get_handler=None,
            patch_handler=None,
            delete_handler=None,
            prestable=None,
            tests=None,
            enabled=True,
    ):
        return await utils_admin.update_endpoint(
            self._api_proxy,
            self._testpoint,
            path=path,
            endpoint_id=endpoint_id,
            dev_team=dev_team,
            duty_group_id=duty_group_id,
            duty_abc=duty_abc,
            put_handler=put_handler,
            post_handler=post_handler,
            get_handler=get_handler,
            patch_handler=patch_handler,
            delete_handler=delete_handler,
            prestable=prestable,
            tests=tests,
            enabled=enabled,
        )

    async def safely_delete_endpoint(self, endpoint_id):
        return await utils_admin.delete_endpoint(
            self._api_proxy, self._testpoint, endpoint_id=endpoint_id,
        )

    async def finalize_endpoint_prestable(
            self,
            endpoint_id,
            resolution,
            force_prestable_revision=None,
            force_recall=1,
    ):
        return await utils_admin.finalize_endpoint_prestable(
            self._api_proxy,
            self._testpoint,
            endpoint_id=endpoint_id,
            resolution=resolution,
            force_prestable_revision=force_prestable_revision,
            force_recall=force_recall,
        )

    async def validate_endpoint(
            self,
            path,
            endpoint_id=None,
            dev_team=None,
            duty_group_id=None,
            duty_abc=None,
            put_handler=None,
            post_handler=None,
            get_handler=None,
            patch_handler=None,
            delete_handler=None,
            tests=None,
    ):
        return await utils_admin.validate_endpoint(
            self._api_proxy,
            path=path,
            endpoint_id=endpoint_id,
            dev_team=dev_team,
            duty_group_id=duty_group_id,
            duty_abc=duty_abc,
            put_handler=put_handler,
            post_handler=post_handler,
            get_handler=get_handler,
            patch_handler=patch_handler,
            delete_handler=delete_handler,
            tests=tests,
        )


@pytest.fixture(name='endpoints')
def _endpoints_fixture(taxi_api_proxy, testpoint):
    return Endpoints(taxi_api_proxy, testpoint)
