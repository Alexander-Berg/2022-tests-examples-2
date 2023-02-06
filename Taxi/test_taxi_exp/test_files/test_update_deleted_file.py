from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import files


async def test_update_deleted_file(taxi_exp_client):
    # 1. post file
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content',
    )
    assert response.status == 200
    first_file_id = (await response.json())['id']

    # 2. downloading file
    content = await files.get_file_body(taxi_exp_client, first_file_id)
    assert content == b'test_content\n'

    # 3. updating file
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content_new',
    )
    assert response.status == 200
    second_file_id = (await response.json())['id']

    # 4. downloading file again
    content = await files.get_file_body(taxi_exp_client, second_file_id)
    assert content == b'test_content_new\n'

    # 6. deleting second version
    response = await files.delete_file(taxi_exp_client, second_file_id, 2)
    assert response.status == 200

    # 7. confirming it was deleted
    response = await files.search_file(taxi_exp_client)
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 1

    # 8. trying to upload a copy of first file body
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content',
    )
    assert response.status == 200

    # 9. checking that it wasn't uploaded again
    assert (await response.json())['id'] == first_file_id

    # 10. trying to upload a copy of second file body
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content_new',
    )
    assert response.status == 200
    third_file_id = (await response.json())['id']

    # 11. checking that it was uploaded again because original was removed
    assert third_file_id != second_file_id

    # 12. confirming it was uploaded
    response = await files.search_file(taxi_exp_client)
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 2

    # 13. deleting everything
    response = await files.delete_file(taxi_exp_client, first_file_id, 1)
    assert response.status == 200
    response = await files.delete_file(taxi_exp_client, third_file_id, 3)
    assert response.status == 200

    # 14. confirming there are no files left
    response = await files.search_file(taxi_exp_client)
    assert response.status == 200
    result = await response.json()
    assert not result['files']

    # 15. uploading a file with all other versions removed
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content_new',
    )
    assert response.status == 200
    fourth_file_id = (await response.json())['id']

    # 16. confirming it was uploaded
    response = await files.search_file(taxi_exp_client)
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 1

    # 17. confirming it has version 4
    file_metadata = await db.get_file(taxi_exp_client.app, fourth_file_id)
    assert file_metadata['version'] == 4
