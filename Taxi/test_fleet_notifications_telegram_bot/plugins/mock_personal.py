import pytest


@pytest.fixture(name='personal')
def _mock_personal(mockserver):
    class PersonalData:
        def __init__(self):
            self.personal_to_tg_id = {}
            self.tg_id_to_personal = {}

        def set_personal_to_tg_id(self, personal_to_tg_id):
            self.personal_to_tg_id = personal_to_tg_id

        def set_tg_id_to_personal(self, tg_id_to_personal):
            self.tg_id_to_personal = tg_id_to_personal

    data = PersonalData()

    @mockserver.json_handler('/personal/v1/telegram_ids/retrieve')
    async def _retrieve(request):
        assert request.method == 'POST'
        pd_id = request.json['id']
        value = data.personal_to_tg_id.get(pd_id)
        if value is not None:
            return {'id': pd_id, 'value': value}
        return mockserver.make_response(status=404)

    @mockserver.json_handler('personal/v1/telegram_ids/store')
    async def _store(request):
        assert request.method == 'POST'
        telegram_id = request.json['value']
        pd_id = data.tg_id_to_personal.get(telegram_id)
        if pd_id is not None:
            return {'id': pd_id, 'value': telegram_id}
        return {'id': 'new_pd_id', 'value': telegram_id}

    return data
