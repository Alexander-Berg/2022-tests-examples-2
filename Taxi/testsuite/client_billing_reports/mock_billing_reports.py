"""
Mock for billing-reports.
"""

import json

import pytest


@pytest.fixture
def mock_billing_reports(mockserver):
    class BillingReportsContext:
        def __init__(self):
            self.doc_select_call_params = []
            self.docs = {}

        def add_doc(
                self,
                response_index,
                doc_id,
                kind,
                external_obj_id,
                external_event_ref,
                event_at,
                process_at,
                service,
                service_user_id,
                data,
                created,
                status,
                tags,
        ):
            doc = {
                'doc_id': doc_id,
                'kind': kind,
                'external_obj_id': external_obj_id,
                'external_event_ref': external_event_ref,
                'event_at': event_at,
                'process_at': process_at,
                'service': service,
                'service_user_id': service_user_id,
                'data': data,
                'created': created,
                'status': status,
                'tags': tags,
            }
            if response_index in self.docs:
                self.docs[response_index].append(doc)
            else:
                self.docs = {response_index: [doc]}

    context = BillingReportsContext()

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def _mock_docs_select(request):
        index = len(context.doc_select_call_params)
        context.doc_select_call_params.append(json.loads(request.get_data()))

        if index in context.docs:
            return {
                'docs': context.docs[index],
                'cursor': {'invalid': 'cursor'},
            }

        return {'docs': [], 'cursor': {'invalid': 'cursor'}}

    return context
