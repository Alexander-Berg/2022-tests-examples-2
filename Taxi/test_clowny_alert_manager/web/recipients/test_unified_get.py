import pytest


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.features_on('enable_clownductor_cache'),
]


@pytest.mark.parametrize(
    'service_id, has_testing',
    [
        pytest.param(139, True, id='with testing'),
        pytest.param(1, False, id='without testing'),
    ],
)
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_TEXT_DESCRIPTIONS={
        'no_info_about_duty_group_description': 'no info custom description',
    },
)
async def test_recipients_unified_get_available_not_defined(
        web_context, unified_recipients, service_id, has_testing,
):
    response = await unified_recipients(
        params={'clown_service_id': service_id},
    )
    assert response == {
        'is_feature_available_for_service': True,
        'is_duty_available': False,
        'unavailable_duty_reason': 'no info custom description',
        'has_testing': has_testing,
    }


async def test_recipients_unified_get_available_unknown_service(
        web_context, unified_recipients,
):
    await unified_recipients(params={'clown_service_id': 999}, status=404)


async def test_recipients_unified_get_available_service_without_stable(
        web_context, unified_recipients,
):
    response = await unified_recipients(params={'clown_service_id': 666})
    assert response == {'is_feature_available_for_service': False}


@pytest.mark.parametrize(
    'service_id, has_testing',
    [
        pytest.param(139, True, id='with testing'),
        pytest.param(1, False, id='without testing'),
    ],
)
async def test_recipients_unified_get_ok(
        web_context, unified_recipients, service_id, has_testing,
):
    await web_context.pg.primary.execute(
        query='INSERT INTO alert_manager.unified_recipients '
        '(clown_service_id, chats, logins, testing_chats, duty, '
        'receive_testing_alerts) '
        f'VALUES ({service_id}, \'{{chat1}}\'::TEXT[], \'{{user1}}\'::TEXT[], '
        '\'{testing_chat}\'::TEXT[], \'off\', FALSE);',
    )
    response = await unified_recipients(
        params={'clown_service_id': service_id},
    )
    assert response == {
        'is_feature_available_for_service': True,
        'is_duty_available': False,
        'unavailable_duty_reason': 'No info about duty group',
        'has_testing': has_testing,
        'unified_recipients': {
            'clown_service_id': service_id,
            'logins': ['user1'],
            'chats': ['chat1'],
            'testing_chats': ['testing_chat'],
            'duty': 'off',
            'receive_testing_alerts': False,
            'do_merge_with_telegram_options': True,
        },
    }
