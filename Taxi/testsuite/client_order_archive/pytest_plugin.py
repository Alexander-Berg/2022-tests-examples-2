import bson
import pytest

from testsuite.utils import callinfo


@pytest.fixture
def order_archive_mock(mockserver):
    order_proc_data = {}
    # pylint: disable=invalid-name
    order_proc_retrieve_timeout = False
    order_proc_bulk_retrieve_timeout = False

    class Mock:
        def __init__(self):
            self.order_proc_retrieve: callinfo.AsyncCallQueue = (
                _order_proc_retrieve
            )
            self.order_proc_bulk_retrieve: callinfo.AsyncCallQueue = (
                _order_proc_bulk_retrieve
            )

        @staticmethod
        def set_order_proc(order_proc_list):
            if isinstance(order_proc_list, dict):
                order_proc_list = [order_proc_list]
            for order_proc in order_proc_list:
                try:
                    order_proc_data[order_proc['_id']] = order_proc
                except KeyError:
                    raise RuntimeError(
                        f'Invalid order_proc without _id: {order_proc}',
                    )

        @staticmethod
        def set_order_proc_retrieve_timeout():
            nonlocal order_proc_retrieve_timeout
            order_proc_retrieve_timeout = True

        @staticmethod
        def set_order_proc_bulk_retrieve_timeout():
            nonlocal order_proc_bulk_retrieve_timeout
            order_proc_bulk_retrieve_timeout = True

    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    @mockserver.json_handler('/order-archive/v2/order_proc/retrieve')
    def _order_proc_retrieve(request):
        if order_proc_retrieve_timeout:
            raise mockserver.TimeoutError()

        def _make_response(doc_id):
            if doc_id not in order_proc_data:
                return mockserver.make_response(status=404)
            bson_doc = bson.BSON.encode({'doc': order_proc_data[doc_id]})
            return mockserver.make_response(
                response=bson_doc, content_type='application/x-bson-binary',
            )

        doc_id = request.json['id']
        # pylint: disable=too-many-nested-blocks
        if doc_id not in order_proc_data:
            if request.json.get('indexes'):
                for order_proc in order_proc_data.values():
                    for index in request.json['indexes']:
                        if index == 'reorder':
                            if (
                                    order_proc.get('reorder', {}).get('id')
                                    == doc_id
                            ):
                                doc_id = order_proc['_id']
                                return _make_response(doc_id)
                        if index == 'alias':
                            for alias in order_proc.get('aliases', []):
                                if alias.get('id') == doc_id:
                                    doc_id = order_proc['_id']
                                    return _make_response(doc_id)
        return _make_response(doc_id)

    @mockserver.json_handler('/order-archive/v1/order_proc/bulk-retrieve')
    def _order_proc_bulk_retrieve(request):
        if order_proc_bulk_retrieve_timeout:
            raise mockserver.TimeoutError()

        doc_ids = request.json['ids']
        result = []
        for doc_id in doc_ids:
            if doc_id in order_proc_data:
                result.append({'doc': order_proc_data[doc_id]})
        return mockserver.make_response(
            response=bson.BSON.encode({'items': result}),
            content_type='application/x-bson-binary',
        )

    return Mock()
