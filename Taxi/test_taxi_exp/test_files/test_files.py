# pylint: disable=too-many-statements
import pytest

from taxi_exp.lib.files import download
from test_taxi_exp.helpers import files


async def test_files(taxi_exp_client):
    # 1. post file
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content',
    )
    assert response.status == 200
    first_file_id = (await response.json())['id']

    # 2. downloading file
    content = await files.get_file_body(taxi_exp_client, first_file_id)
    assert content == b'test_content\n'

    # 3. trying to success put
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content_new',
    )
    assert response.status == 200
    file_id = (await response.json())['id']

    # 4. downloading file again
    content = await files.get_file_body(taxi_exp_client, file_id)
    assert content == b'test_content_new\n'

    # 5. trying to download absent file
    response = await files.get_file_redirect(taxi_exp_client, 'file_2.txt')
    assert response.status == 404

    # 6. uploading the second file
    response = await files.post_file(
        taxi_exp_client, 'file_123.txt', b'test_content_2',
    )
    assert response.status == 200

    # 7. uploading the third file
    response = await files.post_file(
        taxi_exp_client, 'file_456.txt', b'test_content_3',
    )
    assert response.status == 200
    third_file_id = (await response.json())['id']

    # 8. obtaining list of files
    response = await files.search_file(taxi_exp_client, name='le_1')
    assert response.status == 200
    result = await response.json()
    # file_1.txt - 2 version and file_123.txt
    names = [item['name'] for item in result['files']]
    assert len(names) == 3
    assert len(set(names)) == 2

    # 9. obtaining list of files
    response = await files.search_file(taxi_exp_client, name='le_1', limit=1)
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 1

    # 10. obtaining list of files with offset
    response = await files.search_file(taxi_exp_client, offset=1)
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 3
    assert result['files'][0]['name'] == 'file_1.txt'
    assert result['files'][1]['name'] == 'file_123.txt'
    assert result['files'][2]['name'] == 'file_456.txt'

    # 11. obtaining list of files with offset
    response = await files.search_file(taxi_exp_client, offset=2)
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 2
    assert result['files'][0]['name'] == 'file_123.txt'
    assert result['files'][1]['name'] == 'file_456.txt'

    # 12. obtaining list of files
    response = await files.search_file(taxi_exp_client, id=third_file_id)
    assert response.status == 200
    result = await response.json()
    assert result['files'][0]['name'] == 'file_456.txt'

    # 13. trying to delete not existing file
    response = await files.delete_file(
        taxi_exp_client, file_id + 'not_exists', 1,
    )
    assert response.status == 404

    # 14. obtaining list of files
    response = await files.search_file(taxi_exp_client)
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 4

    # 15. trying to delete the first file
    response = await files.delete_file(taxi_exp_client, first_file_id, 2)
    assert response.status == 200

    # 16. obtaining list of files
    response = await files.search_file(taxi_exp_client)
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 3

    # 17. download file with get_transformed handle
    response = await files.get_original_file_by_mds_id(
        taxi_exp_client, file_id,
    )
    content = await response.text()
    assert content == 'test_content_new\n'


@pytest.mark.pgsql('taxi_exp', files=('fill.sql',))
async def test_direct_download_file(taxi_exp_client, monkeypatch):
    body = b'some fake content\nid\nid2'
    file_id = '74807b81b2a9474a931b8eb968e0f838'

    async def _fake_download(file_id, *args, **kwargs):
        return download.DownloadFile(file_id, body, download.DIRECT)

    monkeypatch.setattr(download, 'get_file', _fake_download)

    params = {'id': file_id}
    response = await taxi_exp_client.get(
        '/v1/files/', headers={'YaTaxi-Api-Key': 'secret'}, params=params,
    )
    assert response.status == 200
    assert response.headers.get('Content-Length') == str(len(body))
