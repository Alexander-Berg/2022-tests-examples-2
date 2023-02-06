ENDPOINT = 'user_emails/confirm'


async def test_user_emails_confirm(taxi_user_api, mongodb):
    personal_email_id = '123456dcba00001'
    response = await taxi_user_api.post(
        ENDPOINT,
        json={
            'personal_email_id': personal_email_id,
            'confirmation_code': (
                '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f00001'
            ),
        },
    )
    assert response.status_code == 200
    assert mongodb.user_emails.find_one(
        {'personal_email_id': personal_email_id},
    )['confirmed']


async def test_user_emails_confirm_invalid_confirmation_code(
        taxi_user_api, mongodb,
):
    personal_email_id = '123456dcba00001'
    response = await taxi_user_api.post(
        ENDPOINT,
        json={
            'personal_email_id': personal_email_id,
            'confirmation_code': (
                '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f00002'
            ),
        },
    )
    assert response.status_code == 404
    assert not mongodb.user_emails.find_one(
        {'personal_email_id': personal_email_id},
    )['confirmed']


async def test_user_emails_confirm_not_found_personal_email_id(
        taxi_user_api, mongodb,
):
    personal_email_id = '123456dcba00002'
    response = await taxi_user_api.post(
        ENDPOINT,
        json={
            'personal_email_id': personal_email_id,
            'confirmation_code': (
                '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f00002'
            ),
        },
    )
    assert response.status_code == 404
    assert (
        mongodb.user_emails.find_one({'personal_email_id': personal_email_id})
        is None
    )
