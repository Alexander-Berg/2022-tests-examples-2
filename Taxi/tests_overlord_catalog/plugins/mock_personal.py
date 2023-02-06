import pytest


PERSONAL_TIN_ID = 'personal-tin-id-x123'
DEFAULT_TIN = '123123'


@pytest.fixture(name='personal', autouse=True)
def personal_mock(mockserver):
    class Context:
        def __init__(self):
            self.tins = []

        def add_tins(self, tins):
            self.tins.extend(tins)

    context = Context()

    @mockserver.json_handler('/personal/v1/tins/bulk_store')
    def _handler(request):
        result = {'items': [{'id': PERSONAL_TIN_ID, 'value': DEFAULT_TIN}]}

        for tin in context.tins:
            result['items'].append({'id': PERSONAL_TIN_ID, 'value': tin})

        return result

    return context
