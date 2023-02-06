import pytest

from taxi_corp.clients import corp_billing
from taxi_corp.util import corp_billing_helper


@pytest.mark.config(
    ALLOW_CORP_BILLING_REQUESTS=True, IGNORE_CORP_BILLING_ERRORS=False,
)
async def test_cb_wrapper(taxi_corp_auth_app):
    @corp_billing_helper.cb_wrapper
    async def func_to_wrap(app):
        raise corp_billing.NotFoundError()

    with pytest.raises(corp_billing.NotFoundError):
        await func_to_wrap(taxi_corp_auth_app)


@pytest.mark.config(
    ALLOW_CORP_BILLING_REQUESTS=True, IGNORE_CORP_BILLING_ERRORS=True,
)
async def test_cb_wrapper_ignore(taxi_corp_auth_app):
    errors = 0

    @corp_billing_helper.cb_wrapper
    async def func_to_wrap(app):
        raise corp_billing.NotFoundError()

    try:
        await func_to_wrap(taxi_corp_auth_app)
    except corp_billing.BaseError:
        errors += 1

    assert not errors
