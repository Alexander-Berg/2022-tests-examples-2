async def test_unified_recipients_upsert_apply(
        web_context, unified_recipients_upsert_apply,
):
    await web_context.clownductor_cache.refresh_cache()

    # Add create
    await unified_recipients_upsert_apply(
        data={
            'clown_service_id': 1,
            'chats': ['chat1', 'chat2'],
            'logins': ['alexrasyuk'],
            'testing_chats': ['testing-chat'],
            'duty': 'off',
            'receive_testing_alerts': True,
            'do_merge_with_telegram_options': False,
        },
    )

    rows = await web_context.pg.primary.fetch(
        'SELECT clown_service_id, chats, logins, testing_chats, duty, '
        'receive_testing_alerts, do_merge_with_telegram_options '
        'FROM alert_manager.unified_recipients '
        'ORDER BY clown_service_id;',
    )
    assert len(rows) == 1
    assert dict(rows[0]) == {
        'clown_service_id': 1,
        'chats': ['chat1', 'chat2'],
        'logins': ['alexrasyuk'],
        'testing_chats': ['testing-chat'],
        'duty': 'off',
        'receive_testing_alerts': True,
        'do_merge_with_telegram_options': False,
    }

    # Test update
    await unified_recipients_upsert_apply(
        data={
            'clown_service_id': 1,
            'chats': ['chat3'],
            'logins': ['oboroth'],
            'testing_chats': ['testing-chat2'],
            'duty': 'to_person_on_duty',
            'receive_testing_alerts': False,
            'do_merge_with_telegram_options': False,
        },
    )

    rows = await web_context.pg.primary.fetch(
        'SELECT clown_service_id, chats, logins, testing_chats, duty, '
        'receive_testing_alerts, do_merge_with_telegram_options '
        'FROM alert_manager.unified_recipients '
        'ORDER BY clown_service_id;',
    )
    assert len(rows) == 1
    assert dict(rows[0]) == {
        'clown_service_id': 1,
        'chats': ['chat3'],
        'logins': ['oboroth'],
        'testing_chats': ['testing-chat2'],
        'duty': 'to_person_on_duty',
        'receive_testing_alerts': False,
        'do_merge_with_telegram_options': False,
    }


async def test_unified_recipients_upsert_apply_bad_response(
        web_context, unified_recipients_upsert_apply,
):
    # Test bad duty
    await unified_recipients_upsert_apply(
        data={
            'clown_service_id': 1,
            'chats': ['chat3'],
            'logins': ['oboroth'],
            'testing_chats': ['testing-chat2'],
            'duty': 'on',
            'receive_testing_alerts': False,
            'do_merge_with_telegram_options': False,
        },
        status=400,
    )
