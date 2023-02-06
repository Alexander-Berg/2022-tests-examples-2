async def test_recipients_suggest_from_db(get_recipients_suggest):
    assert sorted(
        (await get_recipients_suggest(params={'clown_service_id': 1}))[
            'recipients'
        ],
    ) == ['chat7', 'user1', 'user2', 'user8']

    assert sorted(
        (await get_recipients_suggest(params={'clown_service_id': 2}))[
            'recipients'
        ],
    ) == ['user3', 'user4', 'user5', 'user6']

    assert sorted(
        (
            await get_recipients_suggest(
                params={'clown_service_id': 2, 'clown_branch_id': 23},
            )
        )['recipients'],
    ) == ['user5', 'user6']


async def test_recipients_suggest_from_db_filter_by_type(
        get_recipients_suggest, mockserver,
):
    @mockserver.handler('/juggler-api/v2/suggest/logins')
    async def _handler(request):
        if request.json['query'] in ['user1', 'user2', 'user8']:
            return mockserver.make_response(
                status=200,
                json={
                    'items': [
                        {'name': request.json['query'], 'type': 'staff_user'},
                    ],
                },
            )
        if request.json['query'] == 'chat7':
            return mockserver.make_response(
                json={'items': [{'name': 'chat7', 'type': 'telegram_chat'}]},
            )
        return mockserver.make_response(json={'items': []})

    # check users only suggest
    response = await get_recipients_suggest(
        params={'clown_service_id': 1, 'recipient_type': 'staff_user'},
    )
    assert sorted(response['recipients']) == ['user1', 'user2', 'user8']

    # check chats only suggest
    response = await get_recipients_suggest(
        params={'clown_service_id': 1, 'recipient_type': 'telegram_chat'},
    )
    assert response == {'recipients': ['chat7']}

    # check empty user_input
    response = await get_recipients_suggest(
        params={
            'clown_service_id': 1,
            'recipient_type': 'telegram_chat',
            'user_input': '',
        },
    )
    assert response == {'recipients': ['chat7']}


async def test_recipients_suggest_from_juggler(
        get_recipients_suggest, mockserver,
):
    @mockserver.handler('/juggler-api/v2/suggest/logins')
    async def _handler(request):
        users = ['abcd', 'abce', 'abd', 'bcd']
        chats = ['abc_chat1', 'chat2']
        recipients = users + chats
        result = []
        if request.json['type'] == 'staff_users':
            result = [
                user
                for user in users
                if user.startswith(request.json['query'])
            ]
        elif request.json['type'] == 'notification_recipients':
            result = [
                recipient
                for recipient in recipients
                if recipient.startswith(request.json['query'])
            ]
        else:
            raise RuntimeError('unknown type: ' + request.json['type'])

        items = []
        for item in result:
            if item in users:
                items.append({'name': item, 'type': 'staff_user'})
            elif item in chats:
                items.append({'name': item, 'type': 'telegram_chat'})

        return mockserver.make_response(json={'items': items})

    # check users suggest
    response = await get_recipients_suggest(
        params={
            'clown_service_id': 1,
            'recipient_type': 'staff_user',
            'user_input': 'abc',
        },
    )
    assert sorted(response['recipients']) == ['abcd', 'abce']

    # check chat suggest
    response = await get_recipients_suggest(
        params={
            'clown_service_id': 1,
            'recipient_type': 'telegram_chat',
            'user_input': 'abc',
        },
    )
    assert sorted(response['recipients']) == ['abc_chat1']

    # check chat suggest
    response = await get_recipients_suggest(
        params={
            'clown_service_id': 1,
            'recipient_type': 'telegram_chat',
            'user_input': 'bcd',
        },
    )
    assert sorted(response['recipients']) == []


async def test_recipients_suggest_bad_request(get_recipients_suggest):
    # check bad recipient type
    await get_recipients_suggest(
        params={
            'clown_service_id': 1,
            'recipient_type': 'staff_users',
            'user_input': 'abc',
        },
        status=400,
    )

    # check no service_id
    await get_recipients_suggest(
        params={'recipient_type': 'staff_user', 'user_input': 'abc'},
        status=400,
    )
