import requests
import uuid
import datetime
import os
import xml.etree.ElementTree as ElementTree
from common_requests.ds_common_create_body import ds_create_ondemand_body, ds_update_ondemand_body
import time
from common_requests.ondemand_transfer import get_activation_landing, get_activation_transfer


PLATFORM_DS_URL = 'http://logistic-platform.taxi.tst.yandex.net/platform/ds'
LOGISTIC_PLATFORM_URL = 'http://logistic-platform.taxi.tst.yandex.net'
CREATE_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/create')
CONFIRM_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/offers/confirm')
EDIT_URL = os.path.join(LOGISTIC_PLATFORM_URL, 'api/b2b/platform/request/edit')
ADMIN_URL = 'https://tariff-editor.taxi.tst.yandex-team.ru/'
ADMIN_REQUEST_PAGE = os.path.join(ADMIN_URL, 'dragon-orders/{}/info?cluster=platform')

AUTHORIZATION = 'beru-employer'
def create_request_ondemand():
    request_id = str(uuid.uuid4())
    delivery_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'+ 'T00:00:00+03:00')
    r = requests.post(
        PLATFORM_DS_URL,
        headers={
            'Authorization': AUTHORIZATION,
            'Content-Type': 'application/xml'
        },
        data=ds_create_ondemand_body(request_id, delivery_date).encode('utf-8')
    )
    r.raise_for_status()
    response_text = r.text
    print('request_id:', request_id)
    response = ElementTree.fromstring(response_text)
    for item in response.findall('./response/orderId'):
        platform_request_id = item.find('partnerId').text
        print('platform_request_id:', platform_request_id,'\n')
        print(f'Request in admin: {ADMIN_REQUEST_PAGE.format(platform_request_id)}')
    return platform_request_id


def send_update_order(platform_request_id):
    r = requests.post(
        PLATFORM_DS_URL,
        headers={
            'Authorization': AUTHORIZATION,
            'Content-Type': 'application/xml'
        },
        data=ds_update_ondemand_body(platform_request_id).encode('utf-8')
    )
    r.raise_for_status()


if __name__ == '__main__':
     platform_request_id = create_request_ondemand()
     print('IN PROGRESS')
     time.sleep(2)
     send_update_order(platform_request_id)
     print('send_update_order')
     time.sleep(2)
     transfer_id = get_activation_landing(platform_request_id)
     print('get_activation_landing')
     time.sleep(1)
     get_activation_transfer(platform_request_id, transfer_id)
     print('DONE')
