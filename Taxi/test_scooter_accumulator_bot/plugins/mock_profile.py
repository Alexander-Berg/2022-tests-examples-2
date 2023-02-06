import aiohttp.web
import pytest


def driver_profiles_id(request):
    assert request.method == 'POST'

    if (
            request.json['driver_phone_in_set'][0]
            == 'd1206262dea04cca9da5525c176c1b90'
    ):
        return {
            'profiles_by_phone': [
                {
                    'driver_phone': 'd1206262dea04cca9da5525c176c1b90',
                    'profiles': [
                        {
                            'data': {
                                'park_id': '5434bf074f8d4239a3a8960416525a10',
                            },
                            'park_driver_profile_id': '5434bf074f8d4239a3a8960416525a10_11e6391c3d2a4673819d1fafe70d982c',  # noqa: E501 line too long
                        },
                        {
                            'data': {'park_id': 'park_id2'},
                            'park_driver_profile_id': 'park_id2_uuid',
                        },
                    ],
                },
            ],
        }

    return {
        'profiles_by_phone': [
            {
                'driver_phone': request.json['driver_phone_in_set'][0],
                'profiles': [],
            },
        ],
    }


def driver_profiles_info(request):
    assert request.method == 'POST'

    if (
            request.json['id_in_set'][0]
            == '5434bf074f8d4239a3a8960416525a10_11e6391c3d2a4673819d1fafe70d982c'  # noqa: E501 line too long
    ):
        if (
                'data.phone_pd_ids' in request.json['projection']
                and 'data.full_name' in request.json['projection']
        ):
            return {
                'profiles': [
                    {
                        'data': {
                            'phone_pd_ids': [
                                {'pd_id': 'd1206262dea04cca9da5525c176c1b90'},
                            ],
                            'full_name': {
                                'first_name': 'Ислам',
                                'last_name': 'Каримов',
                                'middle_name': 'Рахмонович',
                            },
                        },
                        'park_driver_profile_id': '5434bf074f8d4239a3a8960416525a10_11e6391c3d2a4673819d1fafe70d982c',  # noqa: E501 line too long
                    },
                ],
            }
    return {
        'profiles': [{'park_driver_profile_id': request.json['id_in_set'][0]}],
    }


@pytest.fixture
def scooter_accumulator_bot_profile_mocks(
        mock_driver_profiles,
):  # pylint: disable=C0103
    @mock_driver_profiles('/v1/driver/profiles/retrieve_by_phone')
    async def _retrieve_by_phone(request):
        return aiohttp.web.json_response(driver_profiles_id(request))

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve(request):
        return aiohttp.web.json_response(driver_profiles_info(request))
