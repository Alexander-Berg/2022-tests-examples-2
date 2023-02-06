async def test_default(
        dispatcher_access_control,
        statement_list_view,
        statement_list_view_responses,
):
    response = await statement_list_view()
    assert response.status_code == 200, response.text
    assert response.json() == statement_list_view_responses['DEFAULT']


async def test_filter_by_single_status(
        dispatcher_access_control,
        statement_list_view,
        statement_list_view_responses,
):
    response = await statement_list_view(status='executing')
    assert response.status_code == 200, response.text
    assert response.json() == statement_list_view_responses['DEFAULT']


async def test_filter_by_multiple_statuses(
        dispatcher_access_control,
        statement_list_view,
        statement_list_view_responses,
):
    response = await statement_list_view(status='preparing,draft')
    assert response.status_code == 200, response.text
    assert response.json() == statement_list_view_responses['DEFAULT']


async def test_filter_by_search(
        dispatcher_access_control,
        statement_list_view,
        statement_list_view_responses,
):
    response = await statement_list_view(search='1')
    assert response.status_code == 200, response.text
    assert response.json() == statement_list_view_responses['DEFAULT']


async def test_filter_by_everything(
        dispatcher_access_control,
        statement_list_view,
        statement_list_view_responses,
):
    response = await statement_list_view(search='1', status='preparing,draft')
    assert response.status_code == 200, response.text
    assert response.json() == statement_list_view_responses['DEFAULT']


async def test_no_matches(
        dispatcher_access_control,
        statement_list_view,
        statement_list_view_responses,
):
    response = await statement_list_view(search='7', status='preparing,draft')
    assert response.status_code == 200, response.text
    assert response.json() == statement_list_view_responses['DEFAULT']


async def test_pagination(
        dispatcher_access_control,
        statement_list_view,
        statement_list_view_responses,
):
    response = await statement_list_view(
        page_size=3, page_number=1, status='preparing,executing,executed',
    )
    assert response.status_code == 200, response.text
    assert response.json() == statement_list_view_responses['PAGE1']

    response = await statement_list_view(
        page_size=3, page_number=2, status='preparing,executing,executed',
    )
    assert response.status_code == 200, response.text
    assert response.json() == statement_list_view_responses['PAGE2']


async def test_pagination_out_of_bounds(
        dispatcher_access_control,
        statement_list_view,
        statement_list_view_responses,
):
    response = await statement_list_view(page_size=1, page_number=9)
    assert response.status_code == 200, response.text
    assert response.json() == statement_list_view_responses['DEFAULT']
