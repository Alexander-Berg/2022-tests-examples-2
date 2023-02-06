import typing

from taxi_corp_integration_api import consts
from taxi_corp_integration_api.api.common import types
from taxi_corp_integration_api.api.common.payment_methods import base
from taxi_corp_integration_api.api.common.payment_methods.prepare_data import (
    _get_timezone,
)


def mock_prepared_data(
        user: typing.Optional[dict] = None,
        limit: dict = None,
        client: dict = None,
        client_contracts: list = None,
        client_payment_method: types.ClientPaymentMethod = None,
        cost_center_option: typing.Optional[types.CostCenterOption] = None,
        client_categories: typing.List[str] = None,
        client_tariff_plan_series_id: typing.Optional[str] = None,
        zone: typing.Optional[types.TariffSetting] = None,
        zone_status: types.ZoneStatus = types.ZoneStatus.NO_ZONE,
        geo_restrictions: typing.Dict[str, dict] = None,
        department_limits: typing.Optional[
            typing.Dict[str, types.DepartmentBudget]
        ] = None,
        spendings: typing.Optional[types.Spendings] = None,
        departments_list: typing.Optional[typing.List[str]] = None,
        order_info: types.OrderInfo = None,
) -> types.PreparedData:
    return types.PreparedData(
        user=user,
        limit=limit or {},
        client=client
        or {
            '_id': 'client_id',
            'country': 'rus',
            'features': [],
            'services': {},
        },
        client_contracts=types.ClientContracts(client_contracts or []),
        client_payment_method=client_payment_method
        or types.ClientPaymentMethod(types.PaymentMethodType.CORP, None),
        cost_center_option=cost_center_option,
        client_categories=client_categories or [],
        client_tariff_plan_series_id=client_tariff_plan_series_id,
        zone=zone,
        zone_status=zone_status,
        timezone=_get_timezone(types.ZoneData(zone, zone_status), order_info),
        geo_restrictions=geo_restrictions or {},
        department_limits=department_limits,
        spendings=types.Spendings(billing_status=types.BillingStatus.SKIPPED)
        if spendings is None
        else spendings,
        departments_list=departments_list,
    )


def get_checker_instance(
        checker_class,
        context,
        service=consts.ServiceName.TAXI,
        data=None,
        order_info=None,
        locale='ru',
        source_app=None,
        **kwargs,
) -> base.PMChecker:
    return checker_class(
        context,
        service=service,
        data=data,
        order_info=order_info,
        locale=locale,
        source_app=source_app,
        **kwargs,
    )
