import typing

import pytest
import requests

# Generated using ya tool:
#   ya tool tvm unittest user --default 123 --scopes eats:all
USER_TICKET = (
    '3:user:CA0Q__________9_GhgKAgh7EHsaCGVhdHM6YWxsINKF2MwEKAE:InkbJveudHso'
    'lNC3ykQK3umnthMQLs3sqXHnN7TYdIZBc-1pVC1ST1Uskqwrp5Yh1W29gL6ZV9uULajs14F'
    'RDg4tjPKAiAPLpv1YEU5zJAx3J6_br4Z5dj6bZJf81JI-nwW2Sw8CzDBNTnuGcEcId9Ilvg'
    '85lzJcgq3oZuZgFfA'
)

# ya tool tvmknife unittest service -s 404 -d 2345
SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIlAMQqRI:Ta6H2YvxBztdoylkA5V9jOsk_ZoEfPw8MEr1N'
    'et0nrw84sTLgkL3iw6Db4qL7-GifB4Pm06RAoQAseBmmCTdHmYjd0Vk-py6lFR6iQK9QprtN'
    '3Z5_k4fDQ-JLEY9cI6L5qGs2Dcsprt8zTXjmCQPY5CdQnWPOSuU6iu9AqHYWPY'
)


def make_launch_headers(
        session_eater_id,
        passport_eater_id,
        inner_token='inner_token',
        passport_uid='333',
        pass_flags='portal',
        service_ticket=SERVICE_TICKET,
        user_ticket=USER_TICKET,
        login_id='default_login_id',
        device_id='default_device_id',
):
    headers = {
        'X-Ya-Service-Ticket': service_ticket,
        'X-Yandex-UID': passport_uid,
        'X-Ya-User-Ticket': user_ticket,
        'X-YaTaxi-Pass-Flags': pass_flags,
        'X-Eats-Session': inner_token,
        'X-Remote-IP': '127.0.0.1',
        'X-Login-Id': login_id,
        'X-Device-Id': device_id,
    }
    if session_eater_id:
        headers['X-YaTaxi-User'] = 'eats_user_id=' + session_eater_id
    if passport_eater_id:
        headers['X-Eats-Passport-Eater-Id'] = passport_eater_id
    return headers


def make_experiments_headers():
    return {
        'X-Ya-Service-Ticket': SERVICE_TICKET,
        'Content-Type': 'application/json',
    }


class EatsLaunchService:
    def __init__(self):
        self.host = None

    def set_host(self, host: str):
        self.host = host

    def launch_native(
            self,
            session_eater_id: int,
            passport_eater_id: int,
            passport_uid: int,
    ) -> requests.Response:
        return requests.get(
            url=f'{self.host}/eats/v1/launch/v1/native',
            headers=make_launch_headers(
                session_eater_id=str(session_eater_id),
                passport_eater_id=str(passport_eater_id),
                passport_uid=str(passport_uid),
                user_ticket=f'3:user:{passport_uid}',
            ),
        )

    def launch_experiments(
        self, data: typing.Dict,
    ) -> requests.Response:
        return requests.post(
            url=f'{self.host}/eats/v1/launch/v1/experiments',
            headers=make_experiments_headers(),
            json=data,
        )


@pytest.fixture
def launch():
    return EatsLaunchService()
