import pytest

from taxi_billing_docs.common.yt import storage


@pytest.fixture(name='audit_secdist')
def _secdist(simple_secdist):
    simple_secdist['settings_override'] = {
        'YQL_TOKEN': 'common_yql_token',
        'YQL_TOKEN_BILLING_AUDIT': 'yql_token_for_audit',
        'YT_CONFIG': {
            'arnold-billing-audit': {
                'token': 'yt_token_for_audit_on_arnold',
                'prefix': '//yt/audit/arnold/',
                'pickling': {'enable_tmpfs_archive': False},
                'proxy': 'arnold_proxy_for_audit.yt.yandex.net',
            },
            'hahn-billing-audit': {
                'token': 'yt_token_for_audit_on_hahn',
                'prefix': '//yt/audit/hahn/',
                'pickling': {'enable_tmpfs_archive': False},
                'proxy': 'hahn_proxy_for_audit.yt.yandex.net',
            },
        },
    }
    return simple_secdist


def test_secdist_yql_settings(audit_secdist):
    token = storage.get_yql_token(audit_secdist)
    assert token == 'yql_token_for_audit'


def test_yt_settings_arnold(audit_secdist):
    settings = storage.get_yt_settings(audit_secdist, 'arnold')
    assert settings['token'] == 'yt_token_for_audit_on_arnold'
    assert settings['prefix'] == '//yt/audit/arnold/'
    assert settings['proxy'] == 'arnold_proxy_for_audit.yt.yandex.net'


def test_yt_settings_hahn(audit_secdist):
    settings = storage.get_yt_settings(audit_secdist, 'hahn')
    assert settings['token'] == 'yt_token_for_audit_on_hahn'
    assert settings['prefix'] == '//yt/audit/hahn/'
    assert settings['proxy'] == 'hahn_proxy_for_audit.yt.yandex.net'


def test_yt_settings_default(audit_secdist):
    settings = storage.get_yt_settings(audit_secdist, 'abstract')
    assert settings['token'] == ''


def test_yt_prefix_arnold(audit_secdist):
    prefix = storage.get_yt_prefix(audit_secdist, 'arnold')
    assert prefix == '//yt/audit/arnold/unittests/'


def test_yt_prefix_hahn(audit_secdist):
    prefix = storage.get_yt_prefix(audit_secdist, 'hahn')
    assert prefix == '//yt/audit/hahn/unittests/'
