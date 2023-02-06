import typing

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.template.template_info import get_template_data
from order_notify.repositories.template.template_info import TemplateData

BRAND_CONFIGS: typing.List[dict] = [
    {
        'logo_url': 'logo_url_yataxi',
        'map_size': '500,256',
        'from_name': 'Яндекс Go',
        'logo_host': 'go.yandex',
        'taxi_host': 'taxi.yandex.ru',
        'from_email': 'no-reply@taxi.yandex.ru',
        'support_url': 'https://yandex.ru/support/taxi/',
        'campaign_slug': 'OS9GFZ94-YMV1',
        'map_line_color': '3C3C3CFF',
        'map_line_width': 3,
        'map_mid_point_color': 'trackpoint',
        'map_last_point_color': 'comma_solid_blue',
        'map_first_point_color': 'comma_solid_red',
        'map_url': 'https://{}/get-map/1.x/',
    },
    {
        'logo_url': 'logo_url_yango',
        'map_size': '500,256',
        'from_name': 'Yango',
        'taxi_host': 'yango.yandex.com',
        'from_email': 'no-reply@yango.yandex.com',
        'support_url': 'https://yandex.com/support/yango/',
        'campaign_slug': 'OS9GFZ94-YMV1',
        'map_line_color': '3C3C3CFF',
        'map_line_width': 3,
        'map_mid_point_color': 'trackpoint',
        'map_last_point_color': 'comma_solid_blue',
        'map_first_point_color': 'comma_solid_red',
        'map_url': 'https://{}/get-map/1.x/',
    },
]

COUNTRY_CONFIGS: typing.List[dict] = [
    {
        'show_fare_with_vat_only': False,
        'show_ogrn_and_unp': False,
        'show_order_id': False,
        'show_user_fullname': False,
        'receipt_mode': 'receipt',
        'send_pdf': False,
        'extended_uber_report': False,
    },
    {
        'show_fare_with_vat_only': True,
        'show_ogrn_and_unp': False,
        'show_order_id': True,
        'show_user_fullname': False,
        'receipt_mode': 'bill',
        'send_pdf': False,
        'extended_uber_report': False,
    },
    {
        'show_fare_with_vat_only': True,
        'show_ogrn_and_unp': False,
        'show_order_id': True,
        'show_user_fullname': False,
        'receipt_mode': 'receipt',
        'send_pdf': False,
        'extended_uber_report': False,
    },
]


LOCALE_CONFIGS: typing.List[dict] = [
    {},
    {},
    {'from_email': 'yango@yandex.ru', 'from_name': 'paris yango'},
]


@pytest.mark.client_experiments3(
    consumer='order-notify/stq/send_ride_report_mail',
    config_name='order-notify_send_ride_report_brand_template',
    args=[{'name': 'brand', 'type': 'string', 'value': 'yataxi'}],
    value=BRAND_CONFIGS[0],
)
@pytest.mark.client_experiments3(
    consumer='order-notify/stq/send_ride_report_mail',
    config_name='order-notify_send_ride_report_brand_template',
    args=[{'name': 'brand', 'type': 'string', 'value': 'yango'}],
    value=BRAND_CONFIGS[1],
)
@pytest.mark.client_experiments3(
    consumer='order-notify/stq/send_ride_report_mail_country_template',
    config_name='order-notify_send_ride_report_country_template',
    args=[
        {'name': 'brand', 'type': 'string', 'value': 'yataxi'},
        {'name': 'country', 'type': 'string', 'value': 'rus'},
    ],
    value=COUNTRY_CONFIGS[0],
)
@pytest.mark.client_experiments3(
    consumer='order-notify/stq/send_ride_report_mail_locale_template',
    config_name='order-notify_send_ride_report_locale_template',
    args=[
        {'name': 'brand', 'type': 'string', 'value': 'yataxi'},
        {'name': 'locale', 'type': 'string', 'value': 'ru'},
    ],
    value=LOCALE_CONFIGS[0],
)
@pytest.mark.client_experiments3(
    consumer='order-notify/stq/send_ride_report_mail_country_template',
    config_name='order-notify_send_ride_report_country_template',
    args=[
        {'name': 'brand', 'type': 'string', 'value': 'yataxi'},
        {'name': 'country', 'type': 'string', 'value': 'lva'},
    ],
    value=COUNTRY_CONFIGS[1],
)
@pytest.mark.client_experiments3(
    consumer='order-notify/stq/send_ride_report_mail_locale_template',
    config_name='order-notify_send_ride_report_locale_template',
    args=[
        {'name': 'brand', 'type': 'string', 'value': 'yataxi'},
        {'name': 'locale', 'type': 'string', 'value': 'en'},
    ],
    value=LOCALE_CONFIGS[1],
)
@pytest.mark.client_experiments3(
    consumer='order-notify/stq/send_ride_report_mail_country_template',
    config_name='order-notify_send_ride_report_country_template',
    args=[
        {'name': 'brand', 'type': 'string', 'value': 'yango'},
        {'name': 'country', 'type': 'string', 'value': 'fra'},
    ],
    value=COUNTRY_CONFIGS[2],
)
@pytest.mark.client_experiments3(
    consumer='order-notify/stq/send_ride_report_mail_locale_template',
    config_name='order-notify_send_ride_report_locale_template',
    args=[
        {'name': 'brand', 'type': 'string', 'value': 'yango'},
        {'name': 'locale', 'type': 'string', 'value': 'fr'},
    ],
    value=LOCALE_CONFIGS[2],
)
@pytest.mark.parametrize(
    'brand, country, locale, expected_template_data',
    [
        pytest.param(
            'yataxi',
            'rus',
            'ru',
            TemplateData(
                logo_url='logo_url_yataxi',
                map_size='500,256',
                from_name='Яндекс Go',
                logo_host='go.yandex',
                taxi_host='taxi.yandex.ru',
                from_email='no-reply@taxi.yandex.ru',
                support_url='https://yandex.ru/support/taxi/',
                campaign_slug='OS9GFZ94-YMV1',
                show_fare_with_vat_only=False,
                show_ogrn_and_unp=False,
                show_order_id=False,
                show_user_fullname=False,
                receipt_mode='receipt',
                send_pdf=False,
                extended_uber_report=False,
                map_first_point_color='comma_solid_red',
                map_last_point_color='comma_solid_blue',
                map_line_color='3C3C3CFF',
                map_line_width=3,
                map_mid_point_color='trackpoint',
                map_url='https://{}/get-map/1.x/',
            ),
            id='moscow',
        ),
        pytest.param(
            'yataxi',
            'lva',
            'en',
            TemplateData(
                logo_url='logo_url_yataxi',
                map_size='500,256',
                from_name='Яндекс Go',
                logo_host='go.yandex',
                taxi_host='taxi.yandex.ru',
                from_email='no-reply@taxi.yandex.ru',
                support_url='https://yandex.ru/support/taxi/',
                campaign_slug='OS9GFZ94-YMV1',
                show_fare_with_vat_only=True,
                show_ogrn_and_unp=False,
                show_order_id=True,
                show_user_fullname=False,
                receipt_mode='bill',
                send_pdf=False,
                extended_uber_report=False,
                map_first_point_color='comma_solid_red',
                map_last_point_color='comma_solid_blue',
                map_line_color='3C3C3CFF',
                map_line_width=3,
                map_mid_point_color='trackpoint',
                map_url='https://{}/get-map/1.x/',
            ),
            id='riga',
        ),
        pytest.param(
            'yango',
            'fra',
            'fr',
            TemplateData(
                logo_url='logo_url_yango',
                map_size='500,256',
                from_name='paris yango',
                taxi_host='yango.yandex.com',
                from_email='yango@yandex.ru',
                support_url='https://yandex.com/support/yango/',
                campaign_slug='OS9GFZ94-YMV1',
                show_fare_with_vat_only=True,
                show_ogrn_and_unp=False,
                show_order_id=True,
                show_user_fullname=False,
                receipt_mode='receipt',
                send_pdf=False,
                extended_uber_report=False,
                map_first_point_color='comma_solid_red',
                map_last_point_color='comma_solid_blue',
                map_line_color='3C3C3CFF',
                map_line_width=3,
                map_mid_point_color='trackpoint',
                map_url='https://{}/get-map/1.x/',
            ),
            id='paris',
        ),
    ],
)
async def test_get_template(
        stq3_context: stq_context.Context,
        brand,
        country,
        locale,
        expected_template_data,
):
    template_data = await get_template_data(
        context=stq3_context, brand=brand, country=country, locale=locale,
    )
    assert template_data.serialize() == expected_template_data.serialize()
