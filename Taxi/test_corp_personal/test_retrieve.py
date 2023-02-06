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
async def test_retrieve(library_context, pd_type, pd_id, pd_value):

    data = await library_context.corp_personal.retrieve(
        corp_personal_components.PdType(pd_type), pd_id,
    )
    assert data == pd_value


async def test_retrieve_404(library_context):

    data = await library_context.corp_personal.retrieve(
        corp_personal_components.PdType.EMAILS, 'unexpected',
    )
    assert data is None


@pytest.mark.parametrize(
    'pd_type, pd_data',
    [pytest.param('emails', utils.PERSONAL_DATA['emails'], id='emails')],
)
async def test_bulk_retrieve(library_context, pd_type, pd_data):

    pd_ids = [item['id'] for item in pd_data]

    data = await library_context.corp_personal.bulk_retrieve(
        corp_personal_components.PdType(pd_type), pd_ids,
    )

    assert data == {item['id']: item['value'] for item in pd_data}


async def test_bulk_retrieve_404(library_context):

    data = await library_context.corp_personal.bulk_retrieve(
        corp_personal_components.PdType.EMAILS, ['unexpected'],
    )
    assert data == {}
