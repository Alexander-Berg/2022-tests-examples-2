import pytest

from .. import utils_v2


@pytest.fixture(name='claims_creator_v2')
def _claims_creator_v2(taxi_cargo_claims):
    async def _wrapper(**kwargs):
        response, points = await utils_v2.create_claim_v2(
            taxi_cargo_claims, **kwargs,
        )

        class Context:
            def __init__(self, response):
                self.claim_id = response.json()['id']
                self.points = points

        return Context(response)

    return _wrapper
