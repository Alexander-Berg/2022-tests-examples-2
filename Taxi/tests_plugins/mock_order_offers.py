import gzip
import io

import bson
import pytest


def _gzip_decompress(message):
    data = io.BytesIO(message)
    with gzip.GzipFile(mode='rb', fileobj=data) as gzip_file:
        return gzip_file.read()


class OrderOffersContext:
    def __init__(self, mongo_db):
        self._mongo_db = mongo_db

        self._saved_offers = []
        self._offers = {}

        self.mock_save_offer = None
        self.mock_match_offer = None

        self._match_requests = []
        self._offer_id_to_match = None

    def set_offer_to_match(self, offer_id):
        self._offer_id_to_match = offer_id

    def get_matched_offer(self):
        if not self._offer_id_to_match:
            return None

        offer = self._mongo_db.order_offers.find_one(
            {'_id': self._offer_id_to_match},
        )
        # We suppose that the offer with explicitly specified id should exist
        # in a test database, since otherwise there is a risk of a hidden
        # errors that are hard to discover.
        assert offer is not None

        return offer

    def save_offer(self, offer):
        self._saved_offers.append(offer)
        self._offers[offer['_id']] = offer

    @property
    def last_saved_offer(self):
        if self._saved_offers:
            return self._saved_offers[-1]

    def get_offer(self, offer_id):
        return self._offers.get(offer_id)

    def get_user_offer(self, offer_id, user_id):
        offer = self.get_offer(offer_id)

        if offer is not None and offer['user_id'] == user_id:
            return offer

    def save_match_request(self, request):
        self._match_requests.append(request)

    @property
    def last_match_request(self):
        if self._match_requests:
            return self._match_requests[-1]


@pytest.fixture()
def mock_order_offers(mockserver, db):
    context = OrderOffersContext(db)

    @mockserver.handler('/order-offers/v1/save-offer')
    def _mock_save_offer(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/bson'

        content_encoding = request.headers.get('Content-Encoding')
        if content_encoding == 'gzip':
            request_data = _gzip_decompress(request.data)
        else:
            request_data = request.data

        # see TAXIBACKEND-39633 for details
        assert 'Expect' not in request.headers

        request_offer = bson.BSON(request_data).decode()['payload']
        context.save_offer(request_offer)

        return mockserver.make_response(
            bson.BSON.encode({'document': {}}),
            200,
            content_type='application/bson',
        )

    @mockserver.handler('/order-offers/v1/match-offer')
    def _mock_match_offer(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/bson'

        accept_encodings = request.headers.get('Accept-Encoding').split(',')
        assert 'gzip' in accept_encodings

        request_data = request.data
        request_body = bson.BSON(request_data).decode()
        context.save_match_request(request_body)

        assert 'filters' in request_body

        offer = context.get_matched_offer()
        if offer:
            response = {'result': 'match', 'document': offer}
        else:
            response = {'result': 'mismatch'}

        return mockserver.make_response(
            bson.BSON.encode(response), 200, content_type='application/bson',
        )

    context.mock_save_offer = _mock_save_offer
    context.mock_match_offer = _mock_match_offer

    return context
