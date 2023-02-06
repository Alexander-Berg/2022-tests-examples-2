import pytest

from hiring_selfreg_forms.internal import constants
from hiring_selfreg_forms.internal import tools
from test_hiring_selfreg_forms import conftest


GET_EXTERNAL_ID = (
    f'SELECT external_id '
    f'FROM hiring_selfreg_forms.forms_completion '
    f'WHERE form_completion_id=%s'
)
SET_EXTERNAL_ID = (
    f'UPDATE hiring_selfreg_forms.forms_completion '
    f'SET external_id = %s '
    f'WHERE form_completion_id=%s'
)


@pytest.mark.parametrize('request_name', ['default'])
@conftest.main_configuration
async def test_eda_form_data(
        load_json, make_request, perform_auth, request_name, pgsql,
):
    id_ = await perform_auth()
    data = load_json('requests.json')[request_name]
    data[constants.FIELD_FORM_COMPLETION_ID] = id_
    await make_request(
        conftest.ROUTE_EDA_FORM_SUBMIT, data=data, status_code=200,
    )

    # request before auth/phone/check or when don't get external_id
    # from hiring-api
    response_data = await make_request(
        conftest.ROUTE_EDA_FORM_DATA,
        method='get',
        params={constants.FIELD_FORM_COMPLETION_ID: id_},
    )
    assert response_data[constants.FIELD_EXTERNAL_ID] == id_

    external_id = tools.hex_uuid()
    cursor = pgsql['hiring_misc'].cursor()
    cursor.execute(SET_EXTERNAL_ID, (external_id, id_))
    cursor.execute(GET_EXTERNAL_ID, (id_,))

    # request after auth/phone/check or when get external_id from hiring-api
    response_data = await make_request(
        conftest.ROUTE_EDA_FORM_DATA,
        method='get',
        params={constants.FIELD_FORM_COMPLETION_ID: id_},
    )
    assert response_data[constants.FIELD_EXTERNAL_ID] == cursor.fetchone()[0]
