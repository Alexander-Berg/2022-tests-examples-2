import pytest


@pytest.fixture(name='exp_tariff_confirm_usage_enabled')
async def _exp_tariff_confirm_usage_enabled(experiments3, taxi_cargo_pricing):
    async def config(enabled):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_pricing_express_tariff_confirm_usage_enabled',
            consumers=['cargo-pricing/v1/taxi/calc'],
            clauses=[],
            default_value={'enabled': enabled},
        )
        await taxi_cargo_pricing.invalidate_caches()

    return config


@pytest.fixture(name='v1_corp_tariff_confirm_usage')
async def _v1_corp_tariff_confirm_usage(mockserver):
    class Context:
        response_status_code = 200
        mock = None

    ctx = Context()

    @mockserver.json_handler(
        '/cargo-tariffs/cargo-tariffs/express/v1/corp-tariff-confirm-usage',
    )
    def _handle(request):
        assert request.json == {
            'id': 'user_tariff_id',
            'category': 'cargocorp',
        }
        return mockserver.make_response(
            json={}, status=ctx.response_status_code,
        )

    ctx.mock = _handle
    return ctx


async def test_calc_confirm_tariff_usage_enabled(
        v1_calc_creator,
        exp_tariff_confirm_usage_enabled,
        v1_corp_tariff_confirm_usage,
):
    await exp_tariff_confirm_usage_enabled(enabled=True)
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200

    assert v1_corp_tariff_confirm_usage.mock.times_called == 1


async def test_calc_confirm_tariff_usage_disabled(
        v1_calc_creator,
        exp_tariff_confirm_usage_enabled,
        v1_corp_tariff_confirm_usage,
):
    await exp_tariff_confirm_usage_enabled(enabled=False)
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200

    assert v1_corp_tariff_confirm_usage.mock.times_called == 0


async def test_calc_confirm_tariff_usage_error(
        v1_calc_creator,
        exp_tariff_confirm_usage_enabled,
        v1_corp_tariff_confirm_usage,
):
    await exp_tariff_confirm_usage_enabled(enabled=True)
    v1_corp_tariff_confirm_usage.response_status_code = 500
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200
