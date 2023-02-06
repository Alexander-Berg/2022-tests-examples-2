import pytest

from corp_personal import components as corp_personal_components
from test_corp_personal import utils


@pytest.mark.parametrize(
    'pd_type, pd_id, pd_value',
    [
        pytest.param(
            'emails',
            utils.PERSONAL_DATA['emails'][0]['id'],
            utils.PERSONAL_DATA['emails'][0]['value'],
            id='email',
        ),
        pytest.param(
            'phones',
            utils.PERSONAL_DATA['phones'][0]['id'],
            utils.PERSONAL_DATA['phones'][0]['value'],
            id='phone',
        ),
    ],
)
async def test_store(library_context, pd_type, pd_id, pd_value):

    data = await library_context.corp_personal.store(
        corp_personal_components.PdType(pd_type), pd_value,
    )
    assert data == pd_id


@pytest.mark.parametrize(
    'pd_type, pd_data',
    [pytest.param('emails', utils.PERSONAL_DATA['emails'], id='emails')],
)
async def test_bulk_store(library_context, pd_type, pd_data):

    pd_values = [item['value'] for item in pd_data]

    data = await library_context.corp_personal.bulk_store(
        corp_personal_components.PdType(pd_type), pd_values,
    )

    assert data == {item['value']: item['id'] for item in pd_data}
