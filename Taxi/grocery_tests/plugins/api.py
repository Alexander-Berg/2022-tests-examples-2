import pytest
import requests

from grocery_tests import user_model


class GroceryApiService:
    def __init__(self):
        self.host = None

    def set_host(self, host: str):
        self.host = host

    def ping(self) -> requests.Response:
        return requests.get(url=f'{self.host}/ping')

    def service_info(self, lat: float, lon: float) -> requests.Response:
        return requests.post(
            url=f'{self.host}/lavka/v1/api/v1/service-info',
            json={'position': {'location': [lat, lon]}},
        )

    def modes_root(self, user: user_model.GroceryUser) -> requests.Response:
        return requests.post(
            url=f'{self.host}/lavka/v1/api/v1/modes/root',
            json={
                'modes': ['grocery'],
                'position': {'location': user.get_location()},
            },
            headers=user.get_headers(),
        )

    def modes_category(
            self,
            user: user_model.GroceryUser,
            category_id: str,
            offer_id: str,
    ) -> requests.Response:
        return requests.post(
            url=f'{self.host}/lavka/v1/api/v1/modes/category',
            json={
                'modes': ['grocery'],
                'offer_id': offer_id,
                'category_id': category_id,
                'position': {'location': user.get_location()},
            },
            headers=user.get_headers(),
        )


@pytest.fixture
def api():
    return GroceryApiService()
