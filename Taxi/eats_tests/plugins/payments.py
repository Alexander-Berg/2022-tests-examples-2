import pytest
import requests


USER_TICKET = (
    '3:user:CA0Q__________9_GhgKAgh7EHsaCGVhdHM6YWxsINKF2MwEKAE:InkbJveudHso'
    'lNC3ykQK3umnthMQLs3sqXHnN7TYdIZBc-1pVC1ST1Uskqwrp5Yh1W29gL6ZV9uULajs14F'
    'RDg4tjPKAiAPLpv1YEU5zJAx3J6_br4Z5dj6bZJf81JI-nwW2Sw8CzDBNTnuGcEcId9Ilvg'
    '85lzJcgq3oZuZgFfA'
)

SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIlAMQqRI:Ta6H2YvxBztdoylkA5V9jOsk_ZoEfPw8MEr1N'
    'et0nrw84sTLgkL3iw6Db4qL7-GifB4Pm06RAoQAseBmmCTdHmYjd0Vk-py6lFR6iQK9QprtN'
    '3Z5_k4fDQ-JLEY9cI6L5qGs2Dcsprt8zTXjmCQPY5CdQnWPOSuU6iu9AqHYWPY'
)


def make_payments_headers(
        passport_uid='333',
        pass_flags='portal',
        service_ticket=SERVICE_TICKET,
        user_ticket=USER_TICKET,
):
    headers = {
        'User-Agent': 'yandex-taxi/3.129.0.110856 Android/9',
        'X-Ya-Service-Ticket': service_ticket,
        'X-Yandex-UID': passport_uid,
        'X-Ya-User-Ticket': user_ticket,
        'X-YaTaxi-Pass-Flags': pass_flags,
        'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
        'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=yango',
        'Date': 'Tue, 01 Aug 2017 15:00:00 GMT',
    }
    return headers


class EatsPaymentsService:
    def __init__(self):
        self.host = None

    def set_host(self, host: str):
        self.host = host

    def payment_methods_availability(
            self, latitude: float, longitude: float, region_id: int,
    ) -> requests.Response:
        return requests.post(
            url=f'{self.host}/v1/payment-methods-availability',
            json={
                'sender_point': [longitude, latitude],
                'destination_point': [longitude, latitude],
                'order_info': {
                    'currency': 'RUB',
                    'item_sets': [{'amount': '211', 'items_type': 'food'}],
                },
                'place_info': {'accepts_cash': False},
                'region_id': region_id,
            },
            headers=make_payments_headers(),
        )


@pytest.fixture
def payments():
    return EatsPaymentsService()
