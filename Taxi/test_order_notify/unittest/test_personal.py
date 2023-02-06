import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories import personal


@pytest.mark.parametrize(
    'personal_email_id, expected_email',
    [
        pytest.param(
            'eb79288c2399407c8f1319ed6ba5f873',
            'hhr@yandex.ru',
            id='hhr@yandex.ru',
        ),
        pytest.param(
            'ad75d457e3804s11aee24220av6925de',
            'email@email.com',
            id='email@email.com',
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'order-notify'}])
async def test_get_email(
        stq3_context: stq_context.Context,
        mockserver,
        personal_email_id,
        expected_email,
):
    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _retrieve_email(request):
        assert request.json['id'] in (
            'eb79288c2399407c8f1319ed6ba5f873',
            'ad75d457e3804s11aee24220av6925de',
        )
        if request.json['id'] == 'eb79288c2399407c8f1319ed6ba5f873':
            return {
                'id': 'eb79288c2399407c8f1319ed6ba5f873',
                'value': 'hhr@yandex.ru',
            }
        return {
            'id': 'ad75d457e3804s11aee24220av6925de',
            'value': 'email@email.com',
        }

    email = await personal.get_email(
        context=stq3_context, personal_email_id=personal_email_id,
    )
    assert email == expected_email


@pytest.mark.parametrize(
    'personal_phone_id, expected_email',
    [
        pytest.param(
            'eb79288c2399407c8f1319ed6ba5f873',
            '+79850975275',
            id='+79850975275',
        ),
        pytest.param(
            'ad75d457e3804s11aee24220av6925de',
            '+79057387632',
            id='+79057387632',
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'order-notify'}])
async def test_get_phone(
        stq3_context: stq_context.Context,
        mockserver,
        personal_phone_id,
        expected_email,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _retrieve_phone(request):
        assert request.json['id'] in (
            'eb79288c2399407c8f1319ed6ba5f873',
            'ad75d457e3804s11aee24220av6925de',
        )
        if request.json['id'] == 'eb79288c2399407c8f1319ed6ba5f873':
            return {
                'id': 'eb79288c2399407c8f1319ed6ba5f873',
                'value': '+79850975275',
            }
        return {
            'id': 'ad75d457e3804s11aee24220av6925de',
            'value': '+79057387632',
        }

    email = await personal.get_phone(
        context=stq3_context, personal_phone_id=personal_phone_id,
    )
    assert email == expected_email
