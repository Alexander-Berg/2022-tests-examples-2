# import pytest


HEADERS = {
    'User-Agent': 'Taximeter 8.80 (562)',
    'X-Driver-Session': 'session1',
}


async def test_get_permit(
        taxi_driver_profile_view, driver_authorizer, mockserver,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _driver_profiles_list(request):
        return {
            'driver_profiles': [
                {
                    'car': {'id': 'car_id', 'normalized_number': 'А121ТТ77'},
                    'driver_profile': {
                        'id': 'uuid1',
                        'first_name': 'Егор',
                        'last_name': 'Лайд',
                        'middle_name': 'Дмитриевич',
                        'phone_pd_ids': ['phone_pd_id'],
                    },
                },
            ],
            'limit': 1,
            'offset': 0,
            'parks': [{'id': 'db_id1'}],
            'total': 1,
        }

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return {'id': 'phone_pd_id', 'value': '+70001112233'}

    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    response = await taxi_driver_profile_view.get(
        'driver/profile-view/v1/covid-permit',
        params={'park_id': 'db_id1', 'lat': 57.0, 'lon': 37.3},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html'
