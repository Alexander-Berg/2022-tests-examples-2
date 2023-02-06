import pytest

from testsuite.utils import http

from fleet_rent.generated.web import web_context as context_module


_EXPECTED_BODY = """<?xml version="1.0" encoding="UTF-8"?>
<mails>
  <mail encoding="utf-8">
    <from>Яндекс.Такси &lt;no-reply@taxi.yandex.com&gt;</from>
    <reply-to>no-reply@taxi.yandex.com</reply-to>
    <subject encoding="yes">ЗАГОЛОВОК</subject>
    <content-type>text/html; charset="UTF-8"</content-type>
    <parts>
      <part type="text/html">
        <body>
<p>ТЕЛО</p>
<p>------------------------<br/>
НЕ ПИШИ МНЕ</p>
        </body>
      </part>
    </parts>
  </mail>
</mails>"""


@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'park_email_noreply': {'ru': 'НЕ ПИШИ МНЕ'},
        'Yandex': {'ru': 'Яндекс.Такси'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'ПереводМосква'}},
)
async def test_park_mailing_notify_user(
        web_context: context_module.Context,
        mock_sticker,
        park_branding_yandex,
        park_user_stub_factory,
        patch,
):
    @mock_sticker('/send/')
    async def _retrieve(request: http.Request):
        assert request.json == {
            'body': _EXPECTED_BODY,
            'send_to': ['PD_ID'],
            'idempotence_token': 'idempotence_token',
        }
        return {}

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, validate=True, log_extra=None):
        assert data_type == 'emails'
        assert request_value == 'park-director@yandex.ru'
        return {'id': 'PD_ID', 'email': request_value}

    await web_context.external_access.park_mailing.notify(
        idempotence_token='idempotence_token',
        text_subject='ЗАГОЛОВОК',
        text_body='ТЕЛО',
        park_branding=park_branding_yandex,
        park_user_info=park_user_stub_factory(),
        locales=['ru'],
    )
