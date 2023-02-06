import pytest

from eats_support_misc.api import v1_message_for_support_post

TASK_ID = '5b2cae5cb2682a976914c2aa'
EATS_USER_ID = '12345'
USER_PHONE_PD_ID = 'some_user_phone_id'
YANDEX_UID = 'some_yandex_uid'
ORDER_NR = '220703-123456'
MESSAGE = 'Hi, dear eater!'
HIDDEN_COMMENT = 'It\'s Ultima!!!'
CLIENT_EATS_APP_CHAT_TYPE = 'client_eats_app'
EDA_ANDROID_APP_TYPE = 'eda_android'
INTERMEDIATE_MESSAGE = 'We\'re watching, don\'t worry'


@pytest.fixture(autouse=True)
def _default_mock_requests(
        mock_init_chatterbox_task,
        mock_reopen_chatterbox_task,
        mock_add_hidden_comment_to_task,
):
    mock_init_chatterbox_task(
        200,
        {
            'id': TASK_ID,
            'status': v1_message_for_support_post.STATUS_OF_INITIALIZED_TASK,
        },
        CLIENT_EATS_APP_CHAT_TYPE,
        INTERMEDIATE_MESSAGE,
        EATS_USER_ID,
        USER_PHONE_PD_ID,
        ORDER_NR,
        YANDEX_UID,
        v1_message_for_support_post.STATUS_OF_INITIALIZED_TASK,
    )
    mock_reopen_chatterbox_task(
        TASK_ID, v1_message_for_support_post.PROTECTED_STATUSES,
    )
    mock_add_hidden_comment_to_task(TASK_ID, HIDDEN_COMMENT)


@pytest.mark.config(
    EATS_SUPPORT_MISC_CHAT_AND_APP_TYPES_MAPPING=[
        {
            'chat_type': CLIENT_EATS_APP_CHAT_TYPE,
            'app_types': [EDA_ANDROID_APP_TYPE],
        },
    ],
    EATS_SUPPORT_MISC_INTERMEDIATE_PROACTIVE_MESSAGE=INTERMEDIATE_MESSAGE,
    EATS_SUPPORT_MISC_USE_SERVICE_TICKETS=False,
)
@pytest.mark.parametrize(
    (
        'message',
        'hidden_comment',
        'yandex_uid',
        'chatterbox_init_response_status',
        'chatterbox_init_response_data',
    ),
    [
        pytest.param(
            MESSAGE,
            HIDDEN_COMMENT,
            YANDEX_UID,
            200,
            {
                'id': TASK_ID,
                'status': (
                    v1_message_for_support_post.STATUS_OF_INITIALIZED_TASK
                ),
            },
            id='base_case',
        ),
        pytest.param(
            None,
            HIDDEN_COMMENT,
            YANDEX_UID,
            200,
            {
                'id': TASK_ID,
                'status': (
                    v1_message_for_support_post.STATUS_OF_INITIALIZED_TASK
                ),
            },
            id='message_is_null',
        ),
        pytest.param(
            MESSAGE,
            None,
            None,
            200,
            {
                'id': TASK_ID,
                'status': (
                    v1_message_for_support_post.STATUS_OF_INITIALIZED_TASK
                ),
            },
            id='hidden_comment_is_null',
        ),
        pytest.param(
            MESSAGE,
            HIDDEN_COMMENT,
            YANDEX_UID,
            409,
            {'task_id': TASK_ID},
            id='chat_already_exists',
        ),
        pytest.param(
            MESSAGE,
            HIDDEN_COMMENT,
            None,
            409,
            {'task_id': TASK_ID},
            id='yandex_uid_is_null',
        ),
    ],
)
async def test_green_flow(
        # ---- fixtures ----
        mock_init_chatterbox_task,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        message,
        hidden_comment,
        yandex_uid,
        chatterbox_init_response_status,
        chatterbox_init_response_data,
):
    mock_init_chatterbox_task(
        chatterbox_init_response_status,
        chatterbox_init_response_data,
        CLIENT_EATS_APP_CHAT_TYPE,
        message or INTERMEDIATE_MESSAGE,
        EATS_USER_ID,
        USER_PHONE_PD_ID,
        ORDER_NR,
        yandex_uid,
        v1_message_for_support_post.STATUS_OF_INITIALIZED_TASK,
    )

    data = {
        'app_type': EDA_ANDROID_APP_TYPE,
        'eater_id': EATS_USER_ID,
        'eater_phone_id': USER_PHONE_PD_ID,
        'order_nr': ORDER_NR,
    }

    if message is not None:
        data['message'] = message

    if hidden_comment is not None:
        data['hidden_comment'] = hidden_comment

    if yandex_uid is not None:
        data['eater_passport_uid'] = yandex_uid

    response = await taxi_eats_support_misc_web.post(
        '/v1/message-for-support', json=data,
    )

    assert response.status == 200


@pytest.mark.config(
    EATS_SUPPORT_MISC_CHAT_AND_APP_TYPES_MAPPING=[
        {
            'chat_type': CLIENT_EATS_APP_CHAT_TYPE,
            'app_types': [EDA_ANDROID_APP_TYPE],
        },
    ],
    EATS_SUPPORT_MISC_USE_SERVICE_TICKETS=False,
)
async def test_unsupported_app_type(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
):
    data = {
        'app_type': 'UNKNOWN APP TYPE',
        'eater_id': EATS_USER_ID,
        'eater_phone_id': USER_PHONE_PD_ID,
        'order_nr': ORDER_NR,
        'hidden_comment': HIDDEN_COMMENT,
    }

    response = await taxi_eats_support_misc_web.post(
        '/v1/message-for-support', json=data,
    )

    assert response.status == 400
    data = await response.json()
    assert data['code'] == 'unsupported_app_type'


@pytest.mark.config(
    EATS_SUPPORT_MISC_CHAT_AND_APP_TYPES_MAPPING=[
        {
            'chat_type': CLIENT_EATS_APP_CHAT_TYPE,
            'app_types': [EDA_ANDROID_APP_TYPE],
        },
    ],
    EATS_SUPPORT_MISC_USE_SERVICE_TICKETS=False,
)
@pytest.mark.parametrize(
    ('chatterbox_init_response_status', 'expected_status'),
    [(400, 500), (406, 500), (424, 500)],
)
async def test_fail_to_init_chat(
        # ---- fixtures ----
        mock_fail_to_init_task,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        chatterbox_init_response_status,
        expected_status,
):
    mock_fail_to_init_task(
        chatterbox_init_response_status, CLIENT_EATS_APP_CHAT_TYPE,
    )

    data = {
        'app_type': EDA_ANDROID_APP_TYPE,
        'eater_id': EATS_USER_ID,
        'eater_phone_id': USER_PHONE_PD_ID,
        'eater_passport_uid': YANDEX_UID,
        'order_nr': ORDER_NR,
        'hidden_comment': HIDDEN_COMMENT,
    }

    response = await taxi_eats_support_misc_web.post(
        '/v1/message-for-support', json=data,
    )

    assert response.status == expected_status
    data = await response.json()
    assert data['code'] == 'chatterbox_error'


@pytest.mark.config(
    EATS_SUPPORT_MISC_CHAT_AND_APP_TYPES_MAPPING=[
        {
            'chat_type': CLIENT_EATS_APP_CHAT_TYPE,
            'app_types': [EDA_ANDROID_APP_TYPE],
        },
    ],
    EATS_SUPPORT_MISC_INTERMEDIATE_PROACTIVE_MESSAGE=INTERMEDIATE_MESSAGE,
    EATS_SUPPORT_MISC_USE_SERVICE_TICKETS=False,
)
@pytest.mark.parametrize(
    ('chatterbox_reopen_response_status', 'expected_status'),
    [(400, 500), (404, 500), (410, 500)],
)
async def test_fail_to_reopen_chat(
        # ---- fixtures ----
        mock_fail_to_reopen_task,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        chatterbox_reopen_response_status,
        expected_status,
):

    mock_fail_to_reopen_task(chatterbox_reopen_response_status, TASK_ID)

    data = {
        'app_type': EDA_ANDROID_APP_TYPE,
        'eater_id': EATS_USER_ID,
        'eater_phone_id': USER_PHONE_PD_ID,
        'eater_passport_uid': YANDEX_UID,
        'order_nr': ORDER_NR,
        'hidden_comment': HIDDEN_COMMENT,
    }

    response = await taxi_eats_support_misc_web.post(
        '/v1/message-for-support', json=data,
    )

    assert response.status == expected_status
    data = await response.json()
    assert data['code'] == 'chatterbox_error'


@pytest.mark.config(
    EATS_SUPPORT_MISC_CHAT_AND_APP_TYPES_MAPPING=[
        {
            'chat_type': CLIENT_EATS_APP_CHAT_TYPE,
            'app_types': [EDA_ANDROID_APP_TYPE],
        },
    ],
    EATS_SUPPORT_MISC_INTERMEDIATE_PROACTIVE_MESSAGE=INTERMEDIATE_MESSAGE,
    EATS_SUPPORT_MISC_USE_SERVICE_TICKETS=False,
)
@pytest.mark.parametrize(
    ('chatterbox_hidden_comment_response_status', 'expected_status'),
    [(400, 500), (404, 500), (410, 500)],
)
async def test_fail_to_add_hidden_comment(
        # ---- fixtures ----
        mock_fail_to_add_hidden_comment,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        chatterbox_hidden_comment_response_status,
        expected_status,
):

    mock_fail_to_add_hidden_comment(
        chatterbox_hidden_comment_response_status, TASK_ID,
    )

    data = {
        'app_type': EDA_ANDROID_APP_TYPE,
        'eater_id': EATS_USER_ID,
        'eater_phone_id': USER_PHONE_PD_ID,
        'eater_passport_uid': YANDEX_UID,
        'order_nr': ORDER_NR,
        'hidden_comment': HIDDEN_COMMENT,
    }

    response = await taxi_eats_support_misc_web.post(
        '/v1/message-for-support', json=data,
    )

    assert response.status == expected_status
    data = await response.json()
    assert data['code'] == 'chatterbox_error'
