import pytest

from crm_hub.logic import supercontrol


@pytest.mark.config(
    CRM_ADMIN_AUDIENCES_SETTINGS_V2={
        'LavkaUser': {
            'targets_config': [
                {
                    'const_salt': 'salt',
                    'current_period': {
                        'current_control': {
                            'control_percentage': 5,
                            'mechanism': 'exp3',
                            'salt': 'Lavka_RandomHash20210623',
                        },
                        'previous_control_saved_percentage': 0,
                    },
                    'is_active': True,
                    'key': 'phone_pd_id',
                    'label': 'global_control',
                },
            ],
        },
        'EatsUser': {
            'targets_config': [
                {
                    'const_salt': 'salt',
                    'current_period': {
                        'current_control': {
                            'control_percentage': 5,
                            'mechanism': 'exp3',
                            'salt': 'Lavka_RandomHash20210623',
                        },
                        'previous_control': {
                            'control_percentage': 5,
                            'mechanism': 'exp3',
                            'salt': 'Lavka_RandomHash20210623',
                        },
                        'previous_control_saved_percentage': 40,
                    },
                    'previous_period': {
                        'current_control': {
                            'control_percentage': 5,
                            'mechanism': 'exp3',
                            'salt': 'Lavka_RandomHash20210623',
                        },
                        'previous_control': {
                            'control_percentage': 5,
                            'mechanism': 'exp3',
                            'salt': 'Lavka_RandomHash20210623',
                        },
                        'previous_control_saved_percentage': 40,
                    },
                    'is_active': True,
                    'key': 'phone_pd_id',
                    'label': 'global_control',
                },
            ],
        },
        'Driver': {},
    },
    CRM_HUB_SUPERCONTROL_SETTINGS={
        'config_campaign_id_pattern': '^(1234|2345)$',
        'config_enabled_for_all': False,
    },
)
async def test_config_sanity(stq3_context):
    sc_settings = supercontrol.Settings(
        context=stq3_context, campaign_id='1234', campaign_global_control=True,
    )
    assert sc_settings.is_enabled

    sc_settings = supercontrol.Settings(
        context=stq3_context,
        campaign_id='12345',
        campaign_global_control=True,
    )
    assert not sc_settings.is_enabled

    sc_targets = await supercontrol.TargetsConfig.from_config(
        context=stq3_context, entity_type='lavkauser',
    )
    assert sc_targets.targets

    sc_targets = await supercontrol.TargetsConfig.from_config(
        context=stq3_context, entity_type='EatsUser',
    )
    assert sc_targets.targets

    sc_targets = await supercontrol.TargetsConfig.from_config(
        context=stq3_context, entity_type='Unknown',
    )
    assert not sc_targets.targets

    sc_targets = await supercontrol.TargetsConfig.from_config(
        context=stq3_context, entity_type='Driver',
    )
    assert not sc_targets.targets


@pytest.mark.parametrize(
    'value, salt, cond, threshold',
    [
        (
            'e4f8ded736c34b9ca046084f467b76f8',
            'Eda_RandomHash20210623',
            'lt',
            5,
        ),
        (
            '52bf9fa40e3141788157cac050275ea3',
            'Eda_RandomHash20210623',
            'lt',
            5,
        ),
        (
            'cf70f0adfb4e45b8802e2f97423fa34b',
            'Eda_RandomHash20210623',
            'lt',
            5,
        ),
        (
            '31a8284105494982af5f22722364f298',
            'Eda_RandomHash20210623',
            'lt',
            5,
        ),
        (
            '060e70edb31f46f995b9a6e9a08ef016',
            'Eda_RandomHash20210623',
            'ge',
            5,
        ),
        (
            '609c88e1c5874cf796e6c7c897ba702f',
            'Eda_RandomHash20210623',
            'ge',
            5,
        ),
        (
            '98c39090f925402db0f5fad1add112ae',
            'Eda_RandomHash20210623',
            'ge',
            5,
        ),
        (
            '1c7b7517a2864ae0a3680791656762c6',
            'Eda_RandomHash20210623',
            'ge',
            5,
        ),
    ],
)
async def test_exp3_hash(value, salt, cond, threshold):
    result = supercontrol.exp3_hash(
        value=supercontrol.encode(value), salt=supercontrol.encode(salt),
    )
    if cond == 'lt':
        assert result < threshold
    elif cond == 'ge':
        assert result >= threshold
    else:
        assert False


@pytest.mark.parametrize(
    'value, salt, cond, threshold',
    [
        # entries taken from users segment
        ('620bdf373e182e8a2c4a8c1b', 'RandomHash20200311', 'lt', 5),
        ('5fa050ee3e182e8a2c5cc093', 'RandomHash20200311', 'lt', 5),
        ('5eefc06d484d0aeea9e03d19', 'RandomHash20200311', 'lt', 5),
        ('5dad707e211473c8c37e6714', 'RandomHash20200311', 'lt', 5),
        ('5bd9c977d8948a2be4089ecf', 'RandomHash20200311', 'ge', 5),
        ('5baceac98447594c58852e15', 'RandomHash20200311', 'ge', 5),
        ('5d62d545211473c8c3a76bc6', 'RandomHash20200311', 'ge', 5),
        ('5ab60b524e468568cf7c4bfc', 'RandomHash20200311', 'ge', 5),
        # entries taken from drivers segment
        ('5cf78eb6d0be228bcefbaa45', 'RandomHash20200311', 'lt', 5),
        ('5c35f22de301b6012fa3b65f', 'RandomHash20200311', 'lt', 5),
        ('5923f6fa43d523c4a2d4449b', 'RandomHash20200311', 'ge', 5),
        ('5fd60cd721c192841c0c0f48', 'RandomHash20200311', 'ge', 5),
        # entries taken from lavka segment
        ('581eddc50779cf3c0c9e753d', 'RandomHash20200311', 'lt', 5),
        ('5993d66889216ea4ee9f96b4', 'RandomHash20200311', 'lt', 5),
        ('5a2d10503658f98ffb38a153', 'RandomHash20200311', 'lt', 5),
        ('5ba69a9c8447594c58c040c6', 'RandomHash20200311', 'lt', 5),
        ('539e9b54e7e5b1f5397b3888', 'RandomHash20200311', 'ge', 5),
        ('539ebe43e7e5b1f53987f418', 'RandomHash20200311', 'ge', 5),
        ('5659559f85c2850c86c3a4ee', 'RandomHash20200311', 'ge', 5),
        ('58498d50250dd4071d17b26b', 'RandomHash20200311', 'ge', 5),
    ],
)
async def test_murmur_hash(value, salt, cond, threshold):
    result = supercontrol.murmur_hash(
        value=supercontrol.encode(value), salt=supercontrol.encode(salt),
    )
    if cond == 'lt':
        assert result < threshold
    elif cond == 'ge':
        assert result >= threshold
    else:
        assert False
