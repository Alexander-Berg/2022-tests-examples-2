import io

import aiohttp
import xlwt


def prepare_xls(column_items, sheets_count=1):
    book = xlwt.Workbook()
    for i in range(sheets_count):
        sheet = book.add_sheet('Test' + str(i))
        for row, value in enumerate(column_items):
            sheet.write(row, 0, value)

    buf = io.BytesIO()
    book.save(buf)

    return buf.getvalue()


async def test_upload_xls(taxi_personal_py3_web, yt_client, yt_apply):

    writer = aiohttp.MultipartWriter('form-data')
    payload = aiohttp.payload.BytesPayload(
        prepare_xls(['header', 'foo', 'bar', 'baz']),
    )
    payload.set_content_disposition(
        'form-data', name='file', filename='test_table.xls',
    )
    writer.append_payload(payload)
    response = await taxi_personal_py3_web.post(
        '/v1/upload_xls', data=writer, headers=writer.headers,
    )
    assert response.status == 200
    data = await response.json()

    rows = list(yt_client.read_table(data['yt_xls_table_path']))
    assert rows == [{'header': 'foo'}, {'header': 'bar'}, {'header': 'baz'}]


async def test_upload_xls_more_then_one_sheet(
        taxi_personal_py3_web, yt_client, yt_apply,
):

    writer = aiohttp.MultipartWriter('form-data')
    payload = aiohttp.payload.BytesPayload(
        prepare_xls(['header', 'foo', 'bar', 'baz'], sheets_count=2),
    )
    payload.set_content_disposition(
        'form-data', name='file', filename='test_table.xls',
    )
    writer.append_payload(payload)
    response = await taxi_personal_py3_web.post(
        '/v1/upload_xls', data=writer, headers=writer.headers,
    )
    assert response.status == 400
    data = await response.json()
    assert data['code'] == 'INVALID_SHEETS_COUNT'
