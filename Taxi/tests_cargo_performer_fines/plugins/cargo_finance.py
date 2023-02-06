import pytest


@pytest.fixture(name='performer_fines_api_key')
def _performer_fines_api_key():
    return 'OAuth performer-fines-api-key'


@pytest.fixture(name='default_operation_id')
def _default_operation_id():
    return 'operation_id'


@pytest.fixture(name='default_taxi_alias_id')
def _default_taxi_alias_id():
    return 'taxi_alias_id'


@pytest.fixture(name='default_fine_unique_key')
def _default_fine_unique_key():
    return 'fine_unique_key'


@pytest.fixture(name='default_fine_code')
def _default_fine_code():
    return 'cancel_after_confirm'


@pytest.fixture(name='default_ticket')
def _default_ticket():
    return 'TICKET'
