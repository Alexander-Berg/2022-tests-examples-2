import pytest


@pytest.fixture(name='personal')
def _mock_personal(mockserver):
    class PersonalData:
        def __init__(self):
            self.personal_to_tg_id = {}

        def set_personal_to_tg_id(self, personal_to_tg_id):
            self.personal_to_tg_id = personal_to_tg_id

    data = PersonalData()

    @mockserver.json_handler('/personal/v1/telegram_ids/retrieve')
    async def _retrieve(request):
        assert request.method == 'POST'
        pd_id = request.json['id']
        value = data.personal_to_tg_id.get(pd_id)
        if value:
            return {'id': pd_id, 'value': value}
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'Not found value'},
        )

    return data
