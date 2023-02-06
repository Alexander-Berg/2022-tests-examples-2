import requests


STATUS_URL = 'http://logistic-platform.taxi.tst.yandex.net/api/b2b/platform/request/info?dump=eventlog'


def getStatus():
    param = input("Enter your request_id: ")
    r = requests.get(
        STATUS_URL,
        params = {
            'request_id':param
        }
    )
    print(r.elapsed)
    print(r.status_code, r.json())
    if r.status_code != 200:
        print('X-YaRequestId:', r.headers.get('X-YaRequestId'))
    r.raise_for_status()


if __name__ == '__main__':
    getStatus()
