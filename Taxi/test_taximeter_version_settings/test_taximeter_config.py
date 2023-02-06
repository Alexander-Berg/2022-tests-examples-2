import pytest

from taxi import pro_app


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'disabled': ['9.05', '8.99'],
            'feature_support': {
                'android_bug_fix': '9.00',
                'default_feature': '8.80',
            },
            'min': '7.00',
        },
        'taximeter-beta': {
            'disabled': ['9.03', '8.99'],
            'feature_support': {
                'beta_feature': '9.01 (15)',
                'default_feature': '8.80 (13)',
            },
            'min': '8.00',
        },
        'taximeter-ios': {
            'disabled': ['1.03', '1.99 (13)'],
            'feature_support': {
                'default_feature': '1.00',
                'ios_feature': '1.23 (123)',
            },
            'min': '1.00',
        },
    },
)
@pytest.mark.parametrize(
    'user_agent, feature, enabled',
    [
        ('Taximeter-Beta 8.71 (1192)', 'fake_feature', False),
        ('Taximeter-Beta 8.71 (1192)', 'ios_feature', False),
        ('Taximeter 8.79', 'default_feature', False),
        ('Taximeter 8.80', 'default_feature', True),
        ('Taximeter-Beta 8.80', 'default_feature', False),
        ('Taximeter 1.10 (1234) ios', 'ios_feature', False),
        ('Taximeter 1.23 (123) ios', 'ios_feature', True),
        ('Taximeter 1.24 (123) ios', 'ios_feature', True),
        ('Taximeter 9.00 (1192)', 'android_bug_fix', True),
        ('Taximeter-Beta 9.71 (1192)', 'android_bug_fix', True),
        ('Taximeter 1.23 (123) ios', 'android_bug_fix', False),
    ],
)
async def test_taximeter_config(library_context, user_agent, feature, enabled):
    txm_settings = library_context.taximeter_version_settings
    app = pro_app.app_from_user_agent(user_agent)
    assert txm_settings.is_feature_supported(app, feature) == enabled
