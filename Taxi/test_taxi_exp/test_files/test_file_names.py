import pytest

from test_taxi_exp.helpers import files


@pytest.mark.parametrize(
    'name,expected_status',
    [
        ('name with spaces', 400),
        ('русские_имена', 400),
        ('names_with,', 400),
        ('bad/file_name', 400),
        ('name.txt', 200),
        ('true_file_name', 200),
        ('name:other_name', 200),
        ('file_name-other_name', 200),
        ('file_name-0001', 200),
        (
            '%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%B8%'
            'D0%B5%20%D0%B8%D0%BC%D0%B5%D0%BD%D0%B0',
            200,
        ),
    ],
)
async def test_file_names(name, expected_status, taxi_exp_client):
    response = await files.post_file(taxi_exp_client, name, b'test_content')
    assert response.status == expected_status
