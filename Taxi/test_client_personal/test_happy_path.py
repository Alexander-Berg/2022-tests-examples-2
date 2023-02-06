import pytest


@pytest.mark.config(TVM_RULES=[{'src': 'library', 'dst': 'personal'}])
async def test_personal(library_context, mockserver):
    mocked_result = {'value': '+7001112233', 'id': 'personal_id'}
    phone_to_store = '+7001112233'

    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock(request):
        assert request.method == 'POST'
        assert request.json == {'value': phone_to_store, 'validate': True}
        return mocked_result

    result = await library_context.client_personal.store(
        'phones', phone_to_store,
    )

    assert result == {'phone': phone_to_store, 'id': 'personal_id'}
