import aiohttp
import pytest

from taxi.clients import mds_s3


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.now('2020-10-08T08:08:08+00:00')
async def test_v1_upload_csv(
        request_headers,
        patched_tvm_ticket_check,
        patch,
        taxi_billing_orders_client,
):
    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _upload_content(key, body, *args, **kwargs):
        return mds_s3.S3Object(Key='gen_key', ETag=None)

    file_content = b'order_id;sum\n109460a867ed5459b0722838ac32a3f5;1000'
    with aiohttp.MultipartWriter('form-data') as mpwriter:
        payload = aiohttp.payload.BytesPayload(file_content)
        payload.set_content_disposition(
            'form-data', name='csv_file', filename='manual_transactions.csv',
        )
        mpwriter.append_payload(payload)

    headers = request_headers.copy()
    headers.update(mpwriter.headers)
    response = await taxi_billing_orders_client.post(
        '/v1/upload/csv/', data=mpwriter, headers=headers,
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'file_id': 'gen_key',
        'file_url': 'https://test_bucket.test_url/gen_key',
    }
