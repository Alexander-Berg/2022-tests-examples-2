import enum


class NotificationsFields(enum.IntEnum):
    token = 0
    status = 1
    project_id = 2
    template_id = 3
    user_id = 4
    application = 5
    user_device_id = 6
    notification_params = 7
    message_title = 8
    message_body = 9
    deeplink = 10
    api_response = 11
    request = 12
    message_id = 13
    client_type = 14
    sent_at = 15
    sent_transport_type = 16
    personal_phone_id = 17
