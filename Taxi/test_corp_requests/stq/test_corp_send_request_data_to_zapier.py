# pylint: disable=redefined-outer-name
# pylint: disable=too-many-locals
from corp_requests.stq import corp_send_request_data_to_zapier


async def test_send_data_to_zapier(
        mockserver, patch, db, stq3_context, stq, mock_zaiper_add_org,
):
    client_request = {
        'phone': '+79777777777',
        'email': 'a@b.com',
        'name': 'AAA',
        'company': 'BBB',
        'client_id': 'IVB21may1a',
        'country': 'rus',
        'city': 'Moscow',
        'utm': {
            'utm_medium': 'cpc',
            'utm_source': 'yadirect',
            'utm_campaign': '[YT]DT_BB-goal_RU-MOW-MSK_CorpTaxi_1business',
            'utm_term': 'корпоративное такси яндекс',
            'utm_content': '3296395919_6308959046',
            'ya_source': 'businesstaxi',
        },
        'login': 'yandex_login_111',
    }

    await corp_send_request_data_to_zapier.task(stq3_context, client_request)
