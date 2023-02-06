import dataclasses
import datetime

import aiohttp.web

from tests_corp_billing_orders import search_utils


@dataclasses.dataclass
class DocInfo:
    doc: dict
    journal_entries: list
    created: datetime.datetime = dataclasses.field(
        default_factory=datetime.datetime.utcnow,
    )


class Service:  # pylint: disable=R0902
    def __init__(self, keep_history, doc_example, journal_entry_example):
        self._keep_history = keep_history
        self.requests = []
        self._docs = []
        self._docs_data_index = {}
        self._docs_id_index = {}
        self._id_serial = 0
        self._ready_for_processing_ids = set()
        self._processing_status = {}
        self._doc_example = doc_example
        self._journal_entry_example = journal_entry_example

    def docs_create_handler(self, request):
        self._save_request(request)
        data = request.json
        docs = self.find_docs(
            data['kind'], data['external_obj_id'], data['external_event_ref'],
        )
        if docs:
            return docs[0].doc
        return self._add_doc(data)

    def docs_search_handler(self, request):
        self._save_request(request)
        data = request.json
        if 'doc_id' in data:
            doc_info = self.find_by_id(data['doc_id'])
            arr = [doc_info] if doc_info else []
        else:
            arr = self.find_docs(
                data.get('kind'),
                data.get('external_obj_id'),
                data.get('external_event_ref'),
            )
        for doc_info in arr:
            if doc_info.doc['status'] == 'new' and self._is_enough_time_passed(
                    doc_info,
            ):
                doc_info.doc['status'] = 'complete'
        return {'docs': [x.doc for x in arr]}

    def ready_for_processing_handler(self, request):
        self._save_request(request)
        data = request.json
        doc_info = self.find_by_id(data['doc_id'])
        if not doc_info:
            return aiohttp.web.json_response(status=404)

        doc = doc_info.doc
        if doc['doc_id'] not in self._ready_for_processing_ids:
            if self._is_enough_time_passed(doc_info):
                self.mark_ready_for_processing(doc)

        return {
            'ready': doc['doc_id'] in self._ready_for_processing_ids,
            'doc': doc,
        }

    def doc_finish_processing_handler(self, request):
        self._save_request(request)
        data = request.json
        doc_info = self.find_by_id(data['doc_id'])
        if not doc_info:
            return aiohttp.web.json_response(status=404)

        doc = doc_info.doc
        if self._processing_status.get(doc['doc_id'], 'new') == 'new':
            if self._is_enough_time_passed(doc_info):
                self.mark_processed(doc, 'complete')

        status = self._processing_status[doc['doc_id']]
        return {'finished': status in ('complete', 'failed'), 'status': status}

    def doc_journal_search_handler(self, request):
        self._save_request(request)
        data = request.json
        response = []
        found = [self.find_by_id(d['doc_id']) for d in data['docs']]
        for doc_info in filter(bool, found):
            for entry in doc_info.journal_entries:
                obj = self._journal_entry_example.copy()
                obj['amount'] = entry['amount']
                obj['doc_id'] = doc_info.doc['doc_id']
                obj['event_at'] = doc_info.doc['event_at']
                obj['account_id'] = entry['account_id']
                obj['journal_entry_id'] = int(
                    '%d000%d' % (obj['doc_id'], obj['account_id']),
                )
                response.append(obj)
        return {'entries': response}

    def find_docs(
            self, kind=None, external_obj_id=None, external_event_ref=None,
    ):
        docs = []
        for first in search_utils.get_values_by_key(
                self._docs_data_index, kind,
        ):
            for second in search_utils.get_values_by_key(
                    first, external_obj_id,
            ):
                for index in search_utils.get_values_by_key(
                        second, external_event_ref,
                ):
                    docs.append(self._docs[index])
        return docs

    def find_by_id(self, doc_id):
        response = None
        if doc_id in self._docs_id_index:
            index = self._docs_id_index[doc_id]
            response = self._docs[index]
        return response

    def mark_ready_for_processing(self, doc):
        docs = self.find_docs(
            doc['kind'], doc['external_obj_id'], doc['external_event_ref'],
        )
        doc_id = docs[0].doc['doc_id']
        self._ready_for_processing_ids.add(doc_id)

    def mark_processed(self, doc, status):
        docs = self.find_docs(
            doc['kind'], doc['external_obj_id'], doc['external_event_ref'],
        )
        doc_id = docs[0].doc['doc_id']
        self._processing_status[doc_id] = status

    @staticmethod
    def _is_enough_time_passed(doc_info, milliseconds=100):
        delta = datetime.datetime.utcnow() - doc_info.created
        return delta.total_seconds() > milliseconds / 1000.0

    def _add_doc(self, data):
        doc = self._doc_example.copy()
        doc['doc_id'] = self._next_id()
        for key in (
                'kind',
                'external_obj_id',
                'external_event_ref',
                'event_at',
                'service',
        ):
            doc[key] = data[key]
        doc['tags'] = data.get('tags', [])

        doc_info = DocInfo(doc, data['journal_entries'])

        self._docs.append(doc_info)
        index = len(self._docs) - 1

        self._docs_id_index[doc['doc_id']] = index
        self._docs_data_index.setdefault(doc['kind'], {}).setdefault(
            doc['external_obj_id'], {},
        )[data['external_event_ref']] = index

        return doc

    def _next_id(self):
        self._id_serial += 1
        return self._id_serial

    def _save_request(self, request):
        if self._keep_history:
            self.requests.append(request)
