# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=invalid-name
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from authproxy_manager_plugins import *  # noqa: F403 F401


@pytest.fixture
def authproxy_manager(taxi_authproxy_manager):
    class Am:
        async def v1_rules_import(self, *, proxy: str):
            return await taxi_authproxy_manager.post(
                '/v1/rules/import-from-config',
                params={'proxy': proxy},
                headers={'content-type': 'application/json'},
            )

        async def v1_rules_import_draft(self, *, proxy: str):
            return await taxi_authproxy_manager.post(
                '/v1/rules/import-from-config/check-draft',
                params={'proxy': proxy},
                headers={'content-type': 'application/json'},
            )

        async def v1_rules(
                self,
                *,
                proxy: str,
                cursor: Optional[str] = None,
                filters: Optional[object] = None,
                limit: Optional[int] = None,
        ):
            data: Dict[str, Any] = {}
            if cursor:
                data['cursor'] = cursor
            if filters is not None:
                data['filter'] = filters
            if limit is not None:
                data['limit'] = limit

            return await taxi_authproxy_manager.post(
                '/v1/rules',
                json=data,
                params={'proxy': proxy},
                headers={'content-type': 'application/json'},
            )

        async def v1_rules_by_name_get(self, *, proxy: str, name: str):
            return await taxi_authproxy_manager.get(
                '/v1/rules/by-name',
                json='{}',
                params={'proxy': proxy, 'rule-name': name},
                headers={'content-type': 'application/json'},
            )

        async def v1_rules_by_name_put(
                self,
                *,
                proxy: str,
                name: str,
                maintained_by: str,
                rule: dict,
                create: bool = False,
        ):
            params: dict = {
                'proxy': proxy,
                'rule-name': name,
                'maintained-by': maintained_by,
            }
            if create:
                params['create'] = True
            return await taxi_authproxy_manager.put(
                '/v1/rules/by-name',
                json=rule,
                params=params,
                headers={'content-type': 'application/json'},
            )

        async def v1_rules_by_name_delete(
                self, *, proxy: str, name: str, maintained_by: str,
        ):
            return await taxi_authproxy_manager.delete(
                '/v1/rules/by-name',
                params={
                    'proxy': proxy,
                    'rule-name': name,
                    'maintained-by': maintained_by,
                },
                headers={'content-type': 'application/json'},
            )

        async def v1_rules_by_name_check_draft_put(
                self,
                *,
                proxy: str,
                name: str,
                maintained_by: str,
                rule: dict,
                create: bool = False,
        ):
            params: dict = {
                'proxy': proxy,
                'rule-name': name,
                'maintained-by': maintained_by,
            }
            if create:
                params['create'] = True
            return await taxi_authproxy_manager.put(
                '/v1/rules/by-name/check-draft',
                json=rule,
                params=params,
                headers={'content-type': 'application/json'},
            )

        async def v1_rules_by_name_check_draft_delete(
                self, *, proxy: str, name: str, maintained_by: str,
        ):
            return await taxi_authproxy_manager.delete(
                '/v1/rules/by-name/check-draft',
                params={
                    'proxy': proxy,
                    'rule-name': name,
                    'maintained-by': maintained_by,
                },
                headers={'content-type': 'application/json'},
            )

        async def v1_tvm_service(self):
            return await taxi_authproxy_manager.get(
                '/v1/tvm-services',
                json='{}',
                headers={'content-type': 'application/json'},
            )

        async def v1_rules_meta(self, *, proxy: str, rule_names: List[str]):
            return await taxi_authproxy_manager.post(
                '/v1/rules/meta',
                params={'proxy': proxy},
                json={'rule_names': rule_names},
                headers={'content-type': 'application/json'},
            )

    return Am()


@pytest.fixture
def clownductor_mock(mockserver):
    @mockserver.json_handler('/clownductor/v1/projects/')
    async def _mock_projects(request):
        return []

    yield
