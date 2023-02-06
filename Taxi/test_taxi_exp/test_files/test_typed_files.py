import pytest

from test_taxi_exp.helpers import files


@pytest.mark.parametrize(
    'file_type,expected_type,append_is_success,content',
    [
        ('string', 'string', True, b'test_content'),
        ('str', 'string', True, b'test_content'),
        ('int', 'integer', True, b'123455'),
        ('integer', 'integer', True, b'123455'),
        (None, 'string', True, b'test_content'),
        ('bad_type', None, False, b'test_content'),
    ],
)
async def test_file_type(
        file_type, expected_type, append_is_success, content, taxi_exp_client,
):
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', content, file_type=file_type,
    )
    if not append_is_success:
        assert response.status == 400
        return
    assert response.status == 200

    file_id = (await response.json())['id']
    get_response = await files.get_file_redirect(taxi_exp_client, file_id)
    assert get_response.status == 200

    returned_file_type = get_response.headers.get('X-Arg-Type')
    assert returned_file_type == expected_type
