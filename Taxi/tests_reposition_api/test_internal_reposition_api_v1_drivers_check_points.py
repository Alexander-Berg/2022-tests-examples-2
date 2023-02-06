import pytest


@pytest.mark.translations(
    taximeter_messages={
        'home_button.zone': {
            'ru': 'you can\'t setup this home point says Yandex',
        },
    },
)
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'main.sql'])
@pytest.mark.parametrize(
    'mode, points, res',
    [
        (
            'home',
            [[29.1943800, 59.9745800]],
            {
                'checked_points': [
                    {
                        'position': [29.19438, 59.97458],
                        'mode': 'home',
                        'accepted': True,
                    },
                ],
            },
        ),
        (
            'home',
            [[37.41389, 55.97194]],
            {
                'checked_points': [
                    {
                        'position': [37.41389, 55.97194],
                        'mode': 'home',
                        'accepted': False,
                        'message': (
                            'you can\'t setup this home point says Yandex'
                        ),
                    },
                ],
            },
        ),
        (
            'home',
            [
                [29.1943800, 59.9745800],
                [29.1943800, 59.9745801],
                [29.1943800, 59.9745802],
                [29.1943800, 59.9745803],
            ],
            {
                'checked_points': [
                    {
                        'position': [29.1943800, 59.9745800],
                        'mode': 'home',
                        'accepted': True,
                    },
                    {
                        'position': [29.1943800, 59.9745801],
                        'mode': 'home',
                        'accepted': True,
                    },
                    {
                        'position': [29.1943800, 59.9745802],
                        'mode': 'home',
                        'accepted': True,
                    },
                    {
                        'position': [29.1943800, 59.9745803],
                        'mode': 'home',
                        'accepted': True,
                    },
                ],
            },
        ),
        (
            'not_home',
            [[29.1943800, 59.9745800]],
            {
                'checked_points': [
                    {
                        'position': [29.19438, 59.97458],
                        'mode': 'not_home',
                        'accepted': False,
                        'message': 'Invalid mode',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_simple_check(taxi_reposition_api, mode, points, res):
    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v1/drivers/check_points',
        json={
            'check_points': [
                {'mode': mode, 'position': point} for point in points
            ],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == res
