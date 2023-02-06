import requests
import uuid
import datetime
import xml.etree.ElementTree as ElementTree
from common_requests.ds_common_create_body import ds_create_express_body, ds_update_body, ds_call_courier_body
import time


PLATFORM_DS_URL = 'http://logistic-platform.taxi.tst.yandex.net/platform/ds'


def create_request_express():
    request_id = str(uuid.uuid4())
    delivery_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'+ 'T00:00:00+03:00')
    r = requests.post(
        PLATFORM_DS_URL,
        headers={
            'Authorization': 'beru-employer',
            'Content-Type': 'application/xml'
        },
        data=ds_create_express_body(request_id, delivery_date).encode('utf-8')
    )
    r.raise_for_status()
    response_text = r.text
    print('request_id:', request_id)
    response = ElementTree.fromstring(response_text)
    for item in response.findall('./response/orderId'):
        platform_request_id = item.find('partnerId').text
        print('platform_request_id:', platform_request_id)
    return platform_request_id


def send_update_order(platform_request_id):
    r = requests.post(
        PLATFORM_DS_URL,
        headers={
            'Authorization': 'beru-employer',
            'Content-Type': 'application/xml'
        },
        data=ds_update_body(platform_request_id).encode('utf-8')
    )
    r.raise_for_status()


def send_call_courier(platform_request_id):
    r = requests.post(
        PLATFORM_DS_URL,
        headers={
            'Authorization': 'beru-employer',
            'Content-Type': 'application/xml'
        },
        data=ds_call_courier_body(platform_request_id).encode('utf-8')
    )
    r.raise_for_status()


if __name__ == '__main__':
    platform_request_id = create_request_express()
    time.sleep(3)
    send_update_order(platform_request_id)
    time.sleep(3)
    send_call_courier(platform_request_id)
