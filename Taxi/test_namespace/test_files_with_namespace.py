# pylint: disable=too-many-statements

from test_taxi_exp.helpers import files

NAMESPACE = 'market'


async def test_files(taxi_exp_client):
    # 0. post files with no namespace
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content',
    )
    assert response.status == 200

    response = await files.post_file(
        taxi_exp_client, 'file_4.txt', b'some_content',
    )
    assert response.status == 200

    # 1. post file
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content', namespace=NAMESPACE,
    )
    assert response.status == 200
    first_file_id = (await response.json())['id']

    # 2. downloading file
    content = await files.get_file_body(taxi_exp_client, first_file_id)
    assert content == b'test_content\n'

    # 3. trying to success put
    response = await files.post_file(
        taxi_exp_client,
        'file_1.txt',
        b'test_content_new',
        namespace=NAMESPACE,
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
        taxi_exp_client,
        'file_123.txt',
        b'test_content_2',
        namespace=NAMESPACE,
    )
    assert response.status == 200
    second_file_id = (await response.json())['id']

    # 7. uploading the third file
    response = await files.post_file(
        taxi_exp_client,
        'file_456.txt',
        b'test_content_3',
        namespace=NAMESPACE,
    )
    assert response.status == 200
    third_file_id = (await response.json())['id']

    # 8. obtaining list of files with no namespace
    response = await files.search_file(taxi_exp_client, name='le_1')
    assert response.status == 200
    result = await response.json()
    # file_1.txt
    names = [item['name'] for item in result['files']]
    assert len(names) == 1
    assert len(set(names)) == 1

    # 8. obtaining list of files with namespace
    response = await files.search_file(
        taxi_exp_client, name='le_1', namespace=NAMESPACE,
    )
    assert response.status == 200
    result = await response.json()
    # file_1.txt - 2 version and file_123.txt
    names = [item['name'] for item in result['files']]
    assert len(names) == 3
    assert len(set(names)) == 2

    # 9. obtaining list of files
    response = await files.search_file(
        taxi_exp_client, name='le_1', namespace=NAMESPACE, limit=1,
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 1

    # 10. obtaining list of files with offset
    response = await files.search_file(
        taxi_exp_client, namespace=NAMESPACE, offset=1,
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 3
    assert result['files'][0]['name'] == 'file_1.txt'
    assert result['files'][1]['name'] == 'file_123.txt'
    assert result['files'][2]['name'] == 'file_456.txt'

    # 11. obtaining list of files with offset
    response = await files.search_file(
        taxi_exp_client, namespace=NAMESPACE, offset=2,
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 2
    assert result['files'][0]['name'] == 'file_123.txt'
    assert result['files'][1]['name'] == 'file_456.txt'

    # 12. obtaining list of files
    response = await files.search_file(
        taxi_exp_client, namespace=NAMESPACE, id=third_file_id,
    )
    assert response.status == 200
    result = await response.json()
    assert result['files'][0]['name'] == 'file_456.txt'

    # 12. obtaining list of files
    response = await files.search_file(
        taxi_exp_client, namespace=None, id=second_file_id,
    )
    assert response.status == 200
    result = await response.json()
    assert not result['files']

    # 13. trying to delete not existing file
    response = await files.delete_file(
        taxi_exp_client, file_id + 'not_exists', 1,
    )
    assert response.status == 404

    # 14. obtaining list of files
    response = await files.search_file(taxi_exp_client, namespace=NAMESPACE)
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 4

    # 15. trying to delete the first file
    response = await files.delete_file(taxi_exp_client, first_file_id, 2)
    assert response.status == 200

    # 16. obtaining list of files
    response = await files.search_file(taxi_exp_client, namespace=NAMESPACE)
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 3
