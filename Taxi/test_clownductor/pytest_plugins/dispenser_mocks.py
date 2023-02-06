import pytest


@pytest.fixture(name='dispenser_quotas_value')
def _dispenser_quotas_value(relative_load_json):
    return relative_load_json('quotas.json')


@pytest.fixture(name='dispenser_get_quotas')
def _dispenser_get_quotas(mock_dispenser, dispenser_quotas_value):
    @mock_dispenser('/db/api/v2/quotas')
    async def quotas_handler(request):
        assert request.method == 'GET'
        return dispenser_quotas_value

    return quotas_handler


@pytest.fixture(name='dispenser_ssd_quota')
def _dispenser_ssd_quota(mock_dispenser):
    @mock_dispenser(
        r'/db/api/v1/quotas/(?P<abc_slug>[a-zA-Z-_]+)/mdb/ssd/ssd-quota',
        regex=True,
    )
    async def ssd_handler(request, abc_slug):
        assert abc_slug
        assert request.method == 'POST'
        return {}

    return ssd_handler


@pytest.fixture(name='dispenser_ram_quota')
def _dispenser_ram_quota(mock_dispenser):
    @mock_dispenser(
        r'/db/api/v1/quotas/(?P<abc_slug>[a-zA-Z-_]+)/mdb/ram/ram-quota',
        regex=True,
    )
    async def ram_handler(request, abc_slug):
        assert abc_slug
        assert request.method == 'POST'
        return {}

    return ram_handler


@pytest.fixture(name='dispenser_cpu_quota')
def _dispenser_cpu_quota(mock_dispenser):
    @mock_dispenser(
        r'/db/api/v1/quotas/(?P<abc_slug>[a-zA-Z-_]+)/mdb/cpu/cpu-quota',
        regex=True,
    )
    async def cpu_handler(request, abc_slug):
        assert abc_slug
        assert request.method == 'POST'
        return {}

    return cpu_handler
