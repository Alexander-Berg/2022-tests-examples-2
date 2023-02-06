import requests
import time
import json

#Скрипт находит заказы по внешнему ID, получает внутренний id платформы, а так же id заказа в лавке (внешнего оператора) и place id
#После этого отправляет информацию, что по этим заказам надо отправить 50тый чекпоинт.


#Делаем запрос через браузер в админку и копирует из запроса CSRF_token и куки.
#Так же нужно пофиксить конфиг на время выполнения теста https://tariff-editor.taxi.yandex-team.ru/dev/configs/draft/1049394?name=logistic_platform_market_se

URL_request_code = 'https://tariff-editor.taxi.yandex-team.ru/api/admin/api-proxy/logistic/api/admin/request/list/?request_code='
URL_info = 'https://tariff-editor.taxi.yandex-team.ru/api/admin/api-proxy/logistic/api/admin/request/get/?request_id='
URL_gateway = 'http://logistic-platform-market.taxi.yandex.net/api/platform/accept_gateway_event'
CSRF_token = ''
XYaServiceTicket = ''
Cookie = ''


def getRequestIDFromExteenalOrderID(exID):
    r = requests.get(
        URL_request_code + exID + '&csrf_token=' + CSRF_token,
        headers={
            'Cookie': Cookie,
            'X-Ya-Logistic-Cluster': 'platform-market'
        },
        verify=False,
    )
    r.raise_for_status()
    req_id = r.json()['history'][0]['request_id']
    return req_id


def getHistoryInfo(req_id):
    r = requests.get(
        URL_info + request_id + '&csrf_token=' + CSRF_token,
        headers={
            'Cookie': Cookie,
            'X-Ya-Logistic-Cluster': 'platform-market'
        },
        verify=False,
    )
    r.raise_for_status()
    event = r.json()['model']['external_requests'][1]['events'][-1]
    place_id = event['external_place_id']
    order_id = event['external_order_id']

    return req_id, order_id, place_id


def write_to_file(string):
    f = open('./orderId_extOrderId_placeId_list.txt', 'a')
    try:
        f.write(string + '\n')
        f.close()
    finally:
        f.close()


def sendAcceptEvents(req_id, order_id, place_id):

    payload = {
        "class_name": "external_order_finished",
        "event_instant": "2022-07-07T00:00:00+00:00",
        "event_meta": {
            "external_order_finished": {}
        },
        "event_status": "ExecutionWaiting",
        "external_order_id": order_id,
        "external_place_id": place_id,
        "idempotency_token": '{}_{}_{}_fake_delivered'.format(req_id, order_id, place_id),
        "operator_comment": "logistic-platform-gateway",
        "operator_event_type": "delivered",
        "operator_id": "lavka"
    }

    r = requests.post(
        URL_gateway,
        headers={
            'X-Ya-Service-Ticket': XYaServiceTicket
        },
        verify=False,
        data=json.dumps(payload)
    )
    print(r.text)


if __name__ == '__main__':

    f = open('./exID_list.txt', 'r')
    for line in f:
        info = ''
        try:
            line = line.strip()
            request_id = getRequestIDFromExteenalOrderID(line)
            info = getHistoryInfo(request_id)
            sendAcceptEvents(
                info[0],
                info[1],
                info[2]
            )
        except:
            print(line + "error")
            write_to_file(line + str(info))
        finally:
            time.sleep(0)
    f.close()
