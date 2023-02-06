import pytest


@pytest.fixture(name='input_processor_fixtures')
def _input_processor_fixtures(
        stq, taxi_eats_billing_processor, pgsql, load_json, client_info_mock,
):
    class Fixtures:
        def __init__(
                self,
                stq,
                taxi_eats_billing_processor,
                pgsql,
                load_json,
                client_info_mock,
        ):
            self.stq = stq
            self.pgsql = pgsql
            self.taxi_eats_billing_processor = taxi_eats_billing_processor
            self.load_json = load_json
            self.client_info_mock = client_info_mock

    return Fixtures(
        stq, taxi_eats_billing_processor, pgsql, load_json, client_info_mock,
    )
