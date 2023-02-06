import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.localization import tanker

TANKER_KEYS_RUS_YATAXI = {'keys': ['name_title', 'title']}

TRANSLATIONS_RIDE_REPORT = {
    'ride_report.html_body.name_title': {'ru': 'Имя', 'en': 'Name'},
    'ride_report.html_body.title': {'ru': 'Заголовок', 'en': 'Title'},
}


@pytest.mark.client_experiments3(
    consumer='order-notify/stq/send_ride_report_mail',
    config_name='order-notify_send_ride_report_tanker_keys',
    args=[
        {'name': 'brand', 'type': 'string', 'value': 'yataxi'},
        {'name': 'country', 'type': 'string', 'value': 'rus'},
    ],
    value=TANKER_KEYS_RUS_YATAXI,
)
@pytest.mark.parametrize(
    'locale, expected_locale',
    [
        pytest.param('ru', 'ru', id='locale=ru'),
        pytest.param('en', 'en', id='locale=en'),
    ],
)
@pytest.mark.translations(notify=TRANSLATIONS_RIDE_REPORT)
async def test_get_tanker_vars(
        stq3_context: stq_context.Context, locale, expected_locale,
):
    tanker_vars = await tanker.get_html_body_tanker_vars(
        context=stq3_context, brand='yataxi', country='rus', locale=locale,
    )

    assert list(tanker_vars.values()) == [
        translation[locale]
        for key, translation in TRANSLATIONS_RIDE_REPORT.items()
    ]
