import datetime
import time
import uuid

import cached_property

from cargo_newflow import consts
from . import base
from . import cargo_corp


class CargoClaimsClient(base.BaseClient):
    _base_url = 'http://cargo-claims.taxi.tst.yandex.net/'
    _tvm_id = '2017979'

    def __init__(
            self, user, *, corp_client_id=consts.DEFAULT_CORP_CLIENT_ID, yandex_uid=consts.DEFAULT_YANDEX_UID, **kwargs,
    ):
        super().__init__(**kwargs)
        self._user = user
        self._corp_client_id = corp_client_id
        self._yandex_uid = yandex_uid

    def create_claim(self, json):
        return self._perform_post(
            consts.CARGO_API_PREFIX + '/v2/claims/create',
            params={'request_id': uuid.uuid4().hex},
            json=json,
        )

    def accept_claim(self, claim_id):
        return self._perform_post(
            consts.CARGO_API_PREFIX + '/v1/claims/accept',
            params={'claim_id': claim_id},
            json={'version': 1, 'corp_client_id': self._corp_client_id},
        )

    def read_segments_journal(self, cursor):
        json = {}
        if cursor is not None:
            json['cursor'] = cursor

        response = self._perform_post('v1/segments/journal', json=json)

        return response['cursor'], response['entries']

    def get_claim_full(self, claim_id):
        return self._perform_get(
            'v2/claims/full', params={'claim_id': claim_id},
        )

    def get_claim_status(self, claim_id):
        return self._perform_get(
            'v1/claims/cut', params={'claim_id': claim_id},
        )

    def get_segment_info(self, segment_id):
        return self._perform_post(
            'v1/segments/info', params={'segment_id': segment_id},
        )

    def _get_headers(self, headers):
        return {
            **super()._get_headers(headers),
            'X-B2B-Client-Id': self._corp_client_id,
            'Accept-Language': 'ru',
            'X-Yandex-Login': self._user,
            'X-Yandex-UID': self._yandex_uid,
            'X-Cargo-Api-Prefix': consts.CARGO_API_PREFIX,
            'X-B2B-Client-Storage': self._corp_client_storage,
        }

    @cached_property.cached_property 
    def _corp_client_storage(self):
        storage_client = cargo_corp.CargoCorpClient()
        return storage_client.get_corp_client_storage(self._corp_client_id)

    @staticmethod
    def get_next_point(segment):
        min_visit_order_without_resolution = 100500
        for point in segment['points']:
            if (
                    point['resolution']['is_skipped']
                    or point['resolution']['is_visited']
            ):
                continue
            min_visit_order_without_resolution = min(
                min_visit_order_without_resolution, point['visit_order'],
            )
        for point in segment['points']:
            if point['visit_order'] == min_visit_order_without_resolution:
                return point

        assert False, 'Every point have resolution'
        return None

    def wait_for_claim_status(self, claim_id, statuses, wait=10):
        timer = datetime.datetime.now() + datetime.timedelta(seconds=wait)
        while True:
            try:
                claim_status = self.get_claim_status(claim_id)
            except base.HttpNotFoundError:
                continue
            if claim_status['status'] in statuses or datetime.datetime.now() > timer:
                return claim_status
            else:
                time.sleep(1)
                continue

    def wait_for_segment_status(self, segment_id, status, wait=300):
        timer = datetime.datetime.now() + datetime.timedelta(seconds=wait)

        while True:
            segment = self.get_segment_info(segment_id)
            if (segment['status'] == status or datetime.datetime.now() > timer):
                return segment
            else:
                time.sleep(1)
                continue
