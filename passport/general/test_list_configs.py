import json

from hamcrest import (
    assert_that,
    has_items,
    has_key,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.federal_config_api import FederalConfigAPI
from passport.backend.qa.autotests.base.domain import Domain
from passport.backend.qa.autotests.base.settings.federal_config_api import FEDERAL_CONFIG_NAMESPACE
from passport.backend.qa.autotests.base.steps.domain_steps import add_domain
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.qa.autotests.federal_config_api.base_test_data import TEST_CONFIG_BODY_MINIMAL


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(feature='federal-confing-api: list configs', story='add_config')
class FederalConfigApiListConfigsTestCase(BaseTestCase):
    def test_ok(self):
        def add_config(domain: Domain) -> int:
            rv = FederalConfigAPI().post(
                path='/1/config/',
                query_params={
                    'domain_id': domain.domain_id,
                    'namespace': FEDERAL_CONFIG_NAMESPACE,
                },
                form_params=json.dumps(TEST_CONFIG_BODY_MINIMAL),
                expected_http_status=201,
            )
            return rv['config_id']

        with register_portal_account() as user:
            with add_domain(admin_uid=user.uid, domain=user.login + '.ru') as domain_1:
                with add_domain(admin_uid=user.uid, domain=user.login + '.com') as domain_2:
                    with add_domain(admin_uid=user.uid, domain=user.login + '.net') as domain_3:
                        config_id_1 = add_config(domain_1)
                        config_id_2 = add_config(domain_2)
                        config_id_3 = add_config(domain_3)

                        start_idx = 0
                        max_pages = 200

                        seen_config_ids = set()

                        for _ in range(max_pages):
                            rv = FederalConfigAPI().get(
                                path='/1/config/',
                                query_params={
                                    'namespace': FEDERAL_CONFIG_NAMESPACE,
                                    'start_config_id': start_idx,
                                    'limit': 2,
                                },
                            )
                            assert_that(rv, has_key('configs'))
                            if not rv['configs']:
                                break
                            seen_config_ids |= {config['config_id'] for config in rv['configs']}
                            start_idx = max([config['config_id'] for config in rv['configs']]) + 1

                        assert_that(seen_config_ids, has_items(config_id_1, config_id_2, config_id_3))

                        for config_id in [config_id_1, config_id_2, config_id_3]:
                            FederalConfigAPI().delete(
                                path=f'/1/config/by_config_id/{config_id}/',
                                query_params={
                                    'namespace': FEDERAL_CONFIG_NAMESPACE,
                                },
                            )
