from copy import deepcopy


TEST_CLIENT_ID = 'test-client-id'

TEST_CONFIG_BODY_MINIMAL = {
    'saml_config': {
        'single_sign_on_service': {
            'url': 'SSO URL',
            'binding': 'SSO BIND',
        },
        'single_logout_service': {
            'url': 'SLO URL',
            'binding': 'SLO BIND',
        },
        'x509_cert': {
            'new': 'CERT NEW',
            'old': 'CERT OLD',
        },
    },
}

TEST_CONFIG_BODY_FULL = deepcopy(TEST_CONFIG_BODY_MINIMAL)
TEST_CONFIG_BODY_FULL.update(
    oauth_config=dict(
        client_id=TEST_CLIENT_ID,
    ),
    enabled=False,
)
TEST_CONFIG_BODY_FULL['saml_config'].update(
    lowercase_urlencoding=True,
    disable_jit_provisioning=True,
)
