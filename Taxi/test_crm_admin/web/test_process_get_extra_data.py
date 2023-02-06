# import csv
# import io
#
# import pandas
# import pytest
#
# #TODO: activate specs after yt_apply, yt_client will be fixed by testing team
#
#
async def test_campaign_not_found(web_app_client):
    response = await web_app_client.get(
        '/v1/process/extra_data/csv?id=1&column=name_ru',
    )
    assert response.status == 404
    result = await response.json()
    assert result == {'message': 'Campaign 1 was not found'}


#
#
# @pytest.mark.pgsql('crm_admin', files=['init.sql'])
# async def test_bad_column(web_app_client, yt_client):
#     response = await web_app_client.get(
#         '/v1/process/extra_data/csv?id=1&column=name_ru_2',
#     )
#
#     assert response.status == 400
#     data = await response.json()
#     assert data == {'message': 'No data in column "name_ru_2".'}
#
#
# @pytest.mark.pgsql('crm_admin', files=['init.sql'])
# @pytest.mark.yt(static_table_data=['yt_segment_1.yaml'])
# async def test_success_to_csv(web_app_client, yt_apply, yt_client):
#     response = await web_app_client.get(
#         '/v1/process/extra_data/csv?id=1&column=name_ru',
#     )
#
#     headers = response.headers
#     assert headers['Content-Type'] == 'text/csv; charset=utf-8'
#     assert (
#         headers['Content-Disposition']
#         == 'attachment; filename="1_name_ru.csv"'
#     )
#
#     data = await response.text()
#     string_io = io.StringIO(data)
#     reader = csv.reader(string_io)
#
#     expected = (
#         ['name_ru'],
#         ['Азербайджан'],
#         ['Баку'],
#         ['Белоруссия'],
#         ['Благовещенск'],
#         ['Бобруйск'],
#         ['Брест'],
#         ['Брянская область'],
#         ['Кот-д\'Ивуар'],
#         ['Россия'],
#         ['Череповец'],
#     )
#
#     for value in expected:
#         assert next(reader) == value
#
#
# @pytest.mark.pgsql('crm_admin', files=['init.sql'])
# @pytest.mark.yt(static_table_data=['yt_segment_1.yaml'])
# async def test_success_to_xslx(web_app_client, yt_apply, yt_client):
#     response = await web_app_client.get(
#         '/v1/process/extra_data/csv?id=1&column=name_ru&format=xslx',
#     )
#
#     headers = response.headers
#     assert headers['Content-Type'] == 'application/vnd.ms-excel'
#     assert (
#         headers['Content-Disposition']
#         == 'attachment; filename="1_name_ru.xlsx"'
#     )
#
#     data = await response.read()
#     bytes_io = io.BytesIO(data)
#     received = pandas.read_excel(bytes_io)
#
#     names = [
#         'Азербайджан',
#         'Баку',
#         'Белоруссия',
#         'Благовещенск',
#         'Бобруйск',
#         'Брест',
#         'Брянская область',
#         'Кот-д\'Ивуар',
#         'Россия',
#         'Череповец',
#     ]
#     expected = pandas.DataFrame({'name_ru': names})
#
#     assert received.equals(expected)
