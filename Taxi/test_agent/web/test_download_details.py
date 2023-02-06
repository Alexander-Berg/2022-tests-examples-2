import pytest
import xlrd

TRANSLATE = {
    'detail_metric_ticket_code': {'ru': 'Трекер', 'en': 'Ticket code'},
    'detail_metric_dialog_url': {'ru': 'Тикет', 'en': 'Dialog url'},
    'detail_metric_utc_dialog_dttm': {'ru': 'Дата', 'en': 'Date'},
}


async def test_download_empty_data(web_app_client):
    response = await web_app_client.get(
        '/download_details?login=webalex&indicator=widget_taxisupport_qa',
        headers={'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
    )
    assert response.status == 404


async def test_download_403(web_app_client):
    response = await web_app_client.get(
        '/download_details?login=liambaev&indicator=widget_taxisupport_qa',
        headers={'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
    )
    assert response.status == 403


@pytest.mark.now('2022-02-01T00:00:00')
@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
        },
    },
)
@pytest.mark.parametrize(
    'request_login,dst_login,status',
    [('liambaev', 'liambaev', 200), ('device', 'liambaev', 200)],
)
async def test_download_data(web_app_client, request_login, dst_login, status):
    count_rows = 4
    count_cols = 6

    response = await web_app_client.get(
        f'/download_details?login={dst_login}&indicator=widget_taxisupport_qa',
        headers={'X-Yandex-Login': request_login, 'Accept-Language': 'ru-ru'},
    )
    assert response.status == status
    assert response.headers['Content-Type'] == 'application/vnd.ms-excel'
    workbook = xlrd.open_workbook(file_contents=await response.content.read())
    assert workbook.sheet_names() == ['detailing']
    worksheet = workbook.sheet_by_index(0)
    assert worksheet.nrows == count_rows  # count rows + headers
    assert worksheet.ncols == count_cols  # count select fields from db
    assert (
        [worksheet.cell_value(rowx=0, colx=i) for i in range(count_cols)]
        == [
            'Трекер',
            'Тикет',
            'Дата',
            'score_total',
            'auditor_comment',
            'operator_login',
        ]
    )
    assert (
        [
            worksheet.cell_value(rowx=3, colx=i)
            if i not in [2, 6]
            else '2022-01-31 23:00:00'
            for i in range(count_cols)
        ]
        == [
            'TEST_3',
            'dialog_url',
            '2022-01-31 23:00:00',
            0,
            'auditor_comment',
            'liambaev',
        ]
    )
    assert (
        [
            worksheet.cell_value(rowx=2, colx=i)
            if i not in [2, 6]
            else '2022-01-31 22:00:00'
            for i in range(count_cols)
        ]
        == [
            'TEST_2',
            'dialog_url',
            '2022-01-31 22:00:00',
            0,
            'auditor_comment',
            'liambaev',
        ]
    )
    assert (
        [
            worksheet.cell_value(rowx=1, colx=i)
            if i not in [2, 6]
            else '2022-01-31 21:00:00'
            for i in range(count_cols)
        ]
        == [
            'TEST_1',
            'dialog_url_value',
            '2022-01-31 21:00:00',
            0,
            'auditor_comment_value',
            'liambaev',
        ]
    )
