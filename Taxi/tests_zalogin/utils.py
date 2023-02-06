import copy


def build_userinfo(
        token_only=False,
        authorized=False,
        phone_personal_id=None,
        phone_loyal=None,
        application=None,
        last_order_nearest_zone=None,
        name=None,
):
    res = {'token_only': token_only, 'authorized': authorized}
    if phone_personal_id is not None:
        phone = {
            'id': '777777777777777777777777',
            'personal_id': phone_personal_id,
        }
        if phone_loyal is not None:
            phone['loyal'] = phone_loyal
        res['phone'] = phone
    if application is not None:
        res['application'] = application
    if last_order_nearest_zone is not None:
        res['last_order_nearest_zone'] = last_order_nearest_zone
    if name is not None:
        res['name'] = name
    return res


def build_users_request(
        token_only=False,
        authorized=False,
        application='',
        application_version='0.0.0',
        has_ya_plus=False,
        has_cashback_plus=False,
        yandex_staff=False,
        metrica_device_id=None,
):
    request = {
        'token_only': token_only,
        'authorized': authorized,
        'application': application,
        'application_version': application_version,
        'has_ya_plus': has_ya_plus,
        'has_cashback_plus': has_cashback_plus,
        'yandex_staff': yandex_staff,
    }
    if metrica_device_id is not None:
        request['metrica_device_id'] = metrica_device_id
    return request


def build_expected_response(
        authorized=False,
        authorization_confirmed=True,
        phone=None,
        loyal=None,
        last_order_nearest_zone=None,
        name=None,
):
    res = {
        'authorized': authorized,
        'authorization_confirmed': authorization_confirmed,
    }
    if phone is not None:
        res['phone'] = phone
    if loyal is not None:
        res['loyal'] = loyal
    if last_order_nearest_zone is not None:
        res['last_order_nearest_zone'] = last_order_nearest_zone
    if name is not None:
        res['name'] = name
    return res


def with_ids(
        doc,
        user_id=None,
        yandex_uuid=None,
        uuid=None,
        phone_id=None,
        device_id=None,
        metrica_device_id=None,
        personal_phone_id=None,
):
    res = copy.deepcopy(doc)
    if user_id is not None:
        res['id'] = user_id
    if yandex_uuid is not None:
        res['yandex_uuid'] = yandex_uuid
    if uuid is not None:
        res['uuid'] = uuid
    if phone_id is not None:
        res['phone_id'] = phone_id
    if device_id is not None:
        res['device_id'] = device_id
    if metrica_device_id is not None:
        res['metrica_device_id'] = metrica_device_id
    if personal_phone_id is not None:
        res['personal_phone_id'] = personal_phone_id
    return res


def without_fields(doc, *field_names):
    res = copy.deepcopy(doc)
    for field_name in field_names:
        assert field_name in doc
        res.pop(field_name)
    return res
