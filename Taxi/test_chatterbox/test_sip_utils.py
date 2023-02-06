import pytest

from chatterbox.api.sip import utils as sip_utils


@pytest.mark.parametrize(
    ('config', 'expected_phone', 'expected_tenant'),
    [
        (
            {
                '__default__': '+1',
                'sources': [
                    {
                        'phone': '+3',
                        'conditions': {'line': 'second'},
                        'tenant': 'ats2',
                    },
                    {'phone': '+2', 'conditions': {}, 'tenant': 'ats1'},
                ],
            },
            '+2',
            'ats1',
        ),
        ({'__default__': '+1', 'sources': []}, '+1', 'default'),
        (
            {
                '__default__': '+1',
                'sources': [
                    {
                        'phone': '+2',
                        'conditions': {
                            'line': {'#in': ['second', 'third', 'first']},
                        },
                    },
                ],
            },
            '+2',
            'default',
        ),
    ],
)
async def test_get_source_phone(cbox, config, expected_phone, expected_tenant):
    task = {'_id': 'test_task', 'line': 'first'}

    cbox.app.config.CHATTERBOX_SIP_SOURCE_PHONE = config
    source_phone, tenant = sip_utils.get_source_phone(task, cbox.app.config)
    assert source_phone == expected_phone
    assert tenant == expected_tenant
