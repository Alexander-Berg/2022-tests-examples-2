import requests
import os
import re

CANCEL_URL = 'http://logistic-platform.taxi.tst.yandex.net/api/b2b/platform/request/cancel'
AUTHORIZATION = 'f6e848e1201e4a0181e645369fd646e6'

def get_tvm_ticket():
    os.popen('ssh-add', os.devnull)
    a = os.popen('ya tool tvmknife get_service_ticket sshkey --src 2013636 --dst 2024159').read()
    match = re.search(r'(3:serv:.*)$', a)
    ticket = match.group(0)
    return ticket


def offerCancel(request_id):
    r = requests.post(
        CANCEL_URL,
        headers={
            'X-B2B-Client-id': AUTHORIZATION,
            'X-Ya-Service-Ticket': tvm
        },

        json={
            'request_id': request_id
        }
    )
    print(r.json(), r.headers.get('X-YaRequestId'))
    r.raise_for_status()


if __name__ == '__main__':
    request_id = input("Enter your request id: ")
    tvm = get_tvm_ticket()
    offerCancel(request_id)
