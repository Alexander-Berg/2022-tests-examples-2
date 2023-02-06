import json

from hamcrest import (
    assert_that,
    greater_than,
    has_entries,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.federal_config_api import FederalConfigAPI
from passport.backend.qa.autotests.base.settings.federal_config_api import FEDERAL_CONFIG_NAMESPACE
from passport.backend.qa.autotests.base.steps.domain_steps import add_domain
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.qa.autotests.federal_config_api.base_test_data import (
    TEST_CLIENT_ID,
    TEST_CONFIG_BODY_FULL,
    TEST_CONFIG_BODY_MINIMAL,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(feature='federal-confing-api: add config', story='add_config')
class FederalConfigApiAddConfigTestCase(BaseTestCase):
    def test_minimal_ok(self):
        with register_portal_account() as user:
            with add_domain(admin_uid=user.uid, domain=user.login + '.ru') as domain:
                rv = FederalConfigAPI().post(
                    path='/1/config/',
                    query_params={
                        'domain_id': domain.domain_id,
                        'namespace': FEDERAL_CONFIG_NAMESPACE,
                    },
                    form_params=json.dumps(TEST_CONFIG_BODY_MINIMAL),
                    expected_http_status=201,
                )

                assert_that(
                    rv,
                    has_entries(
                        domain_ids=[domain.domain_id],
                        entity_id='',
                        config_id=greater_than(0),
                        enabled=True,
                        saml_config=has_entries(
                            lowercase_urlencoding=False,
                            disable_jit_provisioning=False,
                        ),
                        oauth_config=has_entries(
                            client_id='',
                        ),
                    ),
                )

                config_id = rv['config_id']
                FederalConfigAPI().delete(
                    path=f'/1/config/by_config_id/{config_id}/',
                    query_params={
                        'namespace': FEDERAL_CONFIG_NAMESPACE,
                    },
                    expected_http_status=200,
                )

    def test_full_ok(self):
        with register_portal_account() as user:
            with add_domain(admin_uid=user.uid, domain=user.login + '.ru') as domain:
                rv = FederalConfigAPI().post(
                    path='/1/config/',
                    query_params={
                        'domain_id': domain.domain_id,
                        'namespace': FEDERAL_CONFIG_NAMESPACE,
                    },
                    form_params=json.dumps(TEST_CONFIG_BODY_FULL),
                    expected_http_status=201,
                )

                assert_that(
                    rv,
                    has_entries(
                        domain_ids=[domain.domain_id],
                        entity_id='',
                        config_id=greater_than(0),
                        enabled=False,
                        saml_config=has_entries(
                            lowercase_urlencoding=True,
                            disable_jit_provisioning=True,
                        ),
                        oauth_config=has_entries(
                            client_id=TEST_CLIENT_ID,
                        ),
                    ),
                )

                config_id = rv['config_id']
                FederalConfigAPI().delete(
                    path=f'/1/config/by_config_id/{config_id}/',
                    query_params={
                        'namespace': FEDERAL_CONFIG_NAMESPACE,
                    },
                    expected_http_status=200,
                )
