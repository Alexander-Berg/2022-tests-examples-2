import copy
import json

import pytest


DOCUMENT_ID = '60a517f9b2105d0048d8be50'


@pytest.fixture(name='document_templator')
def mock_document_templator(mockserver):
    class Context:
        def __init__(self):
            self.check_create_receipt_data = None
            self.check_document_by_name_data = None
            self.mocked_error = None

        def mock_error(self, code):
            self.mocked_error = code

        def check_create_receipt(self, **argv):
            self.check_create_receipt_data = copy.deepcopy(argv)

        def check_document_by_name(self, **argv):
            self.check_document_by_name_data = copy.deepcopy(argv)

        def times_dynamic_documents_called(self):
            return _mock_dynamic_documents.times_called

        def times_document_by_name_called(self):
            return _mock_document_by_name.times_called

    context = Context()

    @mockserver.json_handler('/document-templator/v1/dynamic_documents/')
    def _mock_dynamic_documents(request):
        if context.check_create_receipt_data is not None:
            for key, value in context.check_create_receipt_data.items():
                assert request.json[key] == value, key

        if context.mocked_error is not None:
            return mockserver.make_response(
                json.dumps({'code': context.mocked_error, 'message': ''}), 400,
            )

        return {
            'id': DOCUMENT_ID,
            'version': 1,
            'name': 'grocery_paris_payment-28',
            'description': ' ',
            'generated_text': '<h1> hello username </h1>',
            'template_id': '609410e2066f33004e887917',
            'params': [],
        }

    @mockserver.json_handler(
        '/document-templator/v1/dynamic_documents/document_id/',
    )
    def _mock_document_by_name(request):
        if context.check_document_by_name_data is not None:
            for key, value in context.check_document_by_name_data.items():
                assert request.query[key] == value, key

        return {'id': DOCUMENT_ID}

    return context
