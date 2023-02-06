import pytest

from taxi_tests import utils
from taxi_tests.utils import log_requests

TAXIMETER_URL = 'http://taximeter-emulator.taxi.yandex/driver_control'
DRIVER_TRACKSTORY_HOST = 'http://driver-trackstory.taxi.yandex.net/'
FIND_BY_PHONE_ERROR_MSG = 'Failed to get taximeter by phone %s'
MOVE_ERROR_MSG = 'Driver position did not get into %s in time'


class TaximeterControl:
    def __init__(self):
        self._taximeters = []

    def find_by_phone(self, phone):
        for taximeter in self._taximeters:
            if taximeter.phone == phone:
                assert taximeter.stopped
        taximeter = Taximeter(phone)
        self._taximeters.append(taximeter)
        for _ in utils.wait_for(60, FIND_BY_PHONE_ERROR_MSG % phone, sleep=1):
            response = taximeter.info()
            if response['ready']:
                return taximeter
        return None

    def stop_all(self):
        for taximeter in self._taximeters:
            if not taximeter.stopped:
                taximeter.stop()


class Taximeter:
    def __init__(self, phone):
        self.phone = phone
        self.stopped = False

    def _request(self, method, data=None):
        assert not self.stopped
        request = data.copy() if data else {}
        request['phone'] = self.phone
        request['method'] = method
        response = log_requests.post(TAXIMETER_URL, json=request)
        response.raise_for_status()
        return response.json()

    def info(self):
        return self._request('info')

    def move(self, point):
        result = self._request('move', {'point': point})
        position_url = DRIVER_TRACKSTORY_HOST + 'position'
        driver_info = self.info()
        params = {
            'driver_id': driver_info['db_id'] + '_' + driver_info['guid'],
        }
        for _ in utils.wait_for(60, MOVE_ERROR_MSG % point, sleep=1):
            response = log_requests.post(position_url, json=params)
            if response.status_code != 200:
                continue
            data = response.json()
            pos = data['position']
            diff = abs(point[0] - pos['lon']) + abs(point[1] - pos['lat'])
            if diff < 0.001:
                break
            else:
                # move again to send gps/set one more time.
                self._request('move', {'point': point})
        return result

    def requestconfirm(self, status, message=None, cost=None, receipt=None):
        if status == 'waiting':
            status = 3
            if message is None:
                message = 'Точно по адресу'
        elif status == 'transporting':
            status = 5
            if message is None:
                message = 'Поехал'
        elif status == 'complete':
            status = 7
            if message is None:
                message = 'Приехал'
        else:
            raise NotImplementedError
        data = {
            'status': status,
            'message': message,
        }
        if cost is not None:
            data['cost'] = cost
        if receipt is not None:
            data['receipt'] = receipt
        return self._request('requestconfirm', data)

    def stop(self):
        self._request('stop')
        self.stopped = True


@pytest.yield_fixture
def taximeter_control():
    control = TaximeterControl()
    yield control
    control.stop_all()
