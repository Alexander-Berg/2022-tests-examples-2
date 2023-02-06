# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest

EASY_COUNT_PAYMENT = 320
EASY_COUNT_REFUND = 330
EASY_COUNT_LINK = 'https://url.pdf'
EASY_COUNT_DOC_NUMBER = '30024'
EASY_COUNT_DOC_UUID = '7aa39782-c40c-49ea-9083-03edbb5e89a4'
EASY_COUNT_USER_AGENT = 'curl/7.64.1'
EASY_COUNT_TOKEN = 'secret-easy-count'  # From service.yaml
DEVELOPER_EMAIL = 'grocery@yandex-team.ru'

DEFAULT_DOCUMENT = {
    'pdf_link': EASY_COUNT_LINK,
    'pdf_link_copy': 'https://url_copy.pdf',
    'doc_number': EASY_COUNT_DOC_NUMBER,
    'doc_uuid': EASY_COUNT_DOC_UUID,
    'sent_mails': [],
    'success': True,
}


@pytest.fixture(name='easy_count_v2')
def mock_easy_count(mockserver):
    class Context:
        def __init__(self):
            self.create = HandleContext()

    context = Context()

    @mockserver.json_handler('/easy-count/api/createDoc')
    def _mock_create(request):
        handler = context.create
        handler.process(request.json, request.headers)

        return handler.response_with(DEFAULT_DOCUMENT)

    return context
