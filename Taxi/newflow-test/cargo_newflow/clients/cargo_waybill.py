import datetime
import time

from . import base


class CargoWaybillClient(base.BaseClient):
    _base_url = 'http://cargo-dispatch.taxi.tst.yandex.net/'
    _tvm_id = '2017977'

    def __init__(self, user, **kwargs):
        super().__init__(**kwargs)
        self._user = user

    def segment_info(self, segment_id):
        return self._perform_post(
            '/v1/segment/info', params={'segment_id': segment_id},
        )

    def waybill_info(self, waybill_ref):
        return self._perform_post(
            '/v1/waybill/info', params={'waybill_external_ref': waybill_ref},
        )

    def _get_headers(self, headers):
        return {
            **super()._get_headers(headers),
            'Accept-Language': 'ru',
            'X-Yandex-Login': self._user,
            'X-Yandex-UID': '123',
        }

    def _wait_for_segment(self, segment_id, wait, predicate):
        timer = datetime.datetime.now() + datetime.timedelta(seconds=wait)
        segment = None
        while True:
            try:
                segment = self.segment_info(segment_id)
                if datetime.datetime.now() > timer:
                    return segment
                if predicate == 'segment':
                    if segment:
                        return segment
                    else:
                        time.sleep(1)
                if predicate == 'chosen_waybill':
                    if 'chosen_waybill' in segment['dispatch']:
                        return segment

            except base.HttpNotFoundError:
                time.sleep(1)
                continue

    def wait_for_segment_info(self, segment_id, wait=10):
        return self._wait_for_segment(segment_id, wait, predicate='segment')

    def wait_for_chosen_waybill(self, segment_id, wait=300):
        return self._wait_for_segment(
            segment_id, wait, predicate='chosen_waybill')

    def wait_for_taxi_order_info(self, waybill_id, wait=300):
        timer = datetime.datetime.now() + datetime.timedelta(seconds=wait)

        while True:
            waybill = self.waybill_info(waybill_id)
            if ('taxi_order_info' in waybill['execution']
                or datetime.datetime.now() > timer):
                return waybill
            else:
                time.sleep(1)
                continue
