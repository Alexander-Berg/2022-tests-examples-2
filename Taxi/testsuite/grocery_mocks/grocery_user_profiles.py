import dataclasses
from typing import Optional

import pytest

LAVKA_NEWCOMER_DISCOUNT_FRAUD = 'lavka_newcomer_discount_fraud'

BANNED_UID = 'oh_im_bad_really_really_bad'


@dataclasses.dataclass
class UserInfo:
    yandex_uid: Optional[str] = None
    personal_phone_id: Optional[str] = None
    appmetrica_device_id: Optional[str] = None
    session: Optional[str] = None

    def __eq__(self, other):
        if not isinstance(other, UserInfo):
            return NotImplemented
        return (
            (
                self.yandex_uid is not None
                and (self.yandex_uid == other.yandex_uid)
            )
            or (
                self.personal_phone_id is not None
                and (self.personal_phone_id == other.personal_phone_id)
            )
            or (
                self.appmetrica_device_id is not None
                and (self.appmetrica_device_id == other.appmetrica_device_id)
            )
            or (self.session is not None and (self.session == other.session))
        )


@pytest.fixture(name='grocery_user_profiles')
def mock_grocery_user_profiles(mockserver):
    class Context:
        def __init__(self):
            self.is_fraud = True
            self.info_request = None
            self.save_request = None
            self.error_code = None
            self.tags = {'banned': [UserInfo(yandex_uid=BANNED_UID)]}

        def set_error_code(self, code):
            self.error_code = code

        def set_is_fraud(self, is_fraud):
            self.is_fraud = is_fraud

        def times_antifraud_info_called(self):
            return _mock_check_antifraud_info.times_called

        def times_antifraud_save_called(self):
            return _mock_save_antifraud_info.times_called

        def times_check_user_called(self):
            return _mock_check_user_banned.times_called

        def check_info_request(self, **kwargs):
            self.info_request = kwargs

        def check_save_request(self, **kwargs):
            self.save_request = kwargs

        def check_user_tagged_by_tag(self, tag, other_user_info):
            if tag not in self.tags:
                return False
            for user_info in self.tags[tag]:
                if user_info == other_user_info:
                    return True
            return False

        def add_user_banned(
                self,
                appmetrica_device_id=None,
                yandex_uid=None,
                session=None,
                personal_phone_id=None,
        ):
            some_user_info = UserInfo(
                appmetrica_device_id=appmetrica_device_id,
                yandex_uid=yandex_uid,
                personal_phone_id=personal_phone_id,
                session=session,
            )
            if self.check_user_tagged_by_tag('banned', some_user_info):
                raise ValueError('Already banned by some tag')
            self.tags['banned'].append(some_user_info)

    context = Context()

    @mockserver.json_handler(
        '/grocery-user-profiles/internal/antifraud/v1/info',
    )
    def _mock_check_antifraud_info(request):
        if context.info_request is not None:
            for key, value in context.info_request.items():
                assert request.json[key] == value, key

        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )

        if context.is_fraud:
            return {'antifraud_info': {'name': LAVKA_NEWCOMER_DISCOUNT_FRAUD}}
        return {'antifraud_info': {'name': 'test_fraud'}}

    @mockserver.json_handler(
        '/grocery-user-profiles/processing/v1/antifraud/info/save',
    )
    def _mock_save_antifraud_info(request):
        if context.save_request is not None:
            for key, value in context.save_request.items():
                assert request.json[key] == value, key

        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/grocery-user-profiles/internal/v1/user-profiles/v1/check-user',
    )
    def _mock_check_user_banned(request):
        personal_ids = request.json['personal_ids']
        user_info = UserInfo()

        if 'yandex_uid' in personal_ids:
            user_info.yandex_uid = personal_ids['yandex_uid']
        if 'personal_phone_id' in personal_ids:
            user_info.personal_phone_id = personal_ids['personal_phone_id']
        if 'appmetrica_device_id' in personal_ids:
            user_info.appmetrica_device_id = personal_ids[
                'appmetrica_device_id'
            ]
        if 'session' in personal_ids:
            user_info.session = personal_ids['session']

        if context.check_user_tagged_by_tag('banned', user_info):
            return {'banned': True}

        return {'banned': False}

    return context
