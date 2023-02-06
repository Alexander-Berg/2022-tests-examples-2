import pytest

YT_PATH = '//home/unittests/reports'


@pytest.mark.config(KISART_ID_REQUESTS_REPORTS_YT_PATH=YT_PATH)
async def test_reports_sample_csv(
        taxi_kisart_id_requests_web, yt_client, yt_apply, mockserver, load,
):
    @mockserver.handler('/personal/v1/[^/]+/bulk_store', regex=True)
    def _personal(request):
        return mockserver.make_response(
            json={
                'items': [
                    {'id': f'personal:{item["value"]}', 'value': item['value']}
                    for item in request.json['items']
                ],
            },
            status=200,
        )

    expected_table = [
        {
            'msisdn_pdid': 'personal:8888888888',
            'Тип УЗ': 'DRIVER',
            'Статус УЗ': 'ACTIVE',
            'Импортирован': '',
            'kisart_pdid': 'personal:0000555555',
            'licence_pdid': 'personal:6666666666',
            'Регистрация ч/з ЕСИА': 't',
            'Дата отклонения заявки': '',
            'Причина отклонения заявки': '',
        },
        {
            'msisdn_pdid': 'personal:9999999999',
            'Тип УЗ': 'DRIVER',
            'Статус УЗ': 'ACTIVE',
            'Импортирован': '',
            'kisart_pdid': 'personal:0000666666',
            'licence_pdid': 'personal:7777777777',
            'Регистрация ч/з ЕСИА': 't',
            'Дата отклонения заявки': '',
            'Причина отклонения заявки': '',
        },
    ]

    filename = 'test_filename'
    assert not yt_client.exists(f'{YT_PATH}/{filename}')

    response = await taxi_kisart_id_requests_web.post(
        f'save_reports?filename={filename}',
        data=load('reports.csv'),
        headers={'Content-Type': 'text/csv'},
    )
    assert response.status == 200
    assert (
        list(yt_client.read_table(f'{YT_PATH}/{filename}')) == expected_table
    )

    # Add file with the same name
    response = await taxi_kisart_id_requests_web.post(
        f'save_reports?filename={filename}',
        data=load('reports_appended.csv'),
        headers={'Content-Type': 'text/csv'},
    )
    assert response.status == 400
    assert (await response.json())[
        'message'
    ] == 'File with this name was already saved'

    # No changes
    assert (
        list(yt_client.read_table(f'{YT_PATH}/{filename}')) == expected_table
    )


@pytest.mark.config(KISART_ID_REQUESTS_REPORTS_YT_PATH=YT_PATH)
async def test_filter_saved(taxi_kisart_id_requests_web, yt_apply):
    response = await taxi_kisart_id_requests_web.post(
        'filter_saved_reports', json={'filenames': ['1', '2', '3']},
    )
    assert response.status == 200
    assert set(await response.json()) == {'3'}

    response = await taxi_kisart_id_requests_web.post(
        'filter_saved_reports', json={'filenames': ['1', '2']},
    )
    assert response.status == 200
    assert set(await response.json()) == set()

    response = await taxi_kisart_id_requests_web.post(
        'filter_saved_reports', json={'filenames': ['3', '4']},
    )
    assert response.status == 200
    assert set(await response.json()) == {'3', '4'}
