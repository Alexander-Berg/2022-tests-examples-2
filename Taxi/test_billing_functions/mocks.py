from __future__ import annotations

import datetime as dt
import decimal
from typing import Any
from typing import Collection
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import more_itertools

import generated.models.taxi_tariffs as taxi_tariffs_models
from taxi import billing
from taxi.billing import util
from taxi.billing.util import dates

from billing_functions import consts
from billing_functions.repositories import antifraud
from billing_functions.repositories import cities
from billing_functions.repositories import commission_agreements
from billing_functions.repositories import contracts
from billing_functions.repositories import currency_rates
from billing_functions.repositories import driver_fix_rules
from billing_functions.repositories import driver_mode_settings
from billing_functions.repositories import driver_mode_subscriptions
from billing_functions.repositories import support_info
from billing_functions.repositories import tariffs


_CityId = str
_CurrencyPair = str
_Date = str
_Decimal = str
_MultiplierType = str
_ParkId = str


class Cities(cities.Repository):
    def __init__(
            self,
            cities_data: Dict[_CityId, Dict[str, Any]],
            parks: Dict[_ParkId, _CityId],
    ):
        self._cities = {
            key: self._parse_city(value) for key, value in cities_data.items()
        }
        self._parks = dict(parks)

    async def fetch_park_city_id(self, park_id: str) -> str:
        return self._parks[park_id]

    async def fetch(self, city_id) -> cities.City:
        city = self._cities.get(city_id)
        if city:
            return city
        raise cities.CityNotFoundError(f'City {city_id} not found')

    @staticmethod
    def _parse_city(city_data: Dict[str, Any]) -> cities.City:
        return cities.City(
            country_code=city_data['country_code'],
            donate_multipliers=Cities._parse_donate_multipliers(
                city_data['donate_multipliers'],
            ),
        )

    @staticmethod
    def _parse_donate_multipliers(
            data: Dict[_MultiplierType, _Decimal],
    ) -> cities.DonateMultipliers:
        return cities.DonateMultipliers(
            default=util.call_or_none(data.get('default'), decimal.Decimal),
            discounts=util.call_or_none(
                data.get('discounts'), decimal.Decimal,
            ),
        )


class Contracts(contracts.Repository):
    def __init__(self, data: List[dict]):
        self._items = [self._parse_contract(item) for item in data]

    @staticmethod
    def _parse_contract(data: dict) -> contracts.Contract:
        return contracts.Contract(
            id=data['id'],
            currency=data['currency'],
            firm_id=data['firm_id'],
            service_ids=data['service_ids'],
            begin=dates.parse_datetime(data['begin']),
            is_yandex_bank_enabled=data['is_yandex_bank_enabled'],
        )

    async def get_contracts(
            self,
            billing_client_id: str,
            active_ts: dt.datetime,
            actual_ts: dt.datetime,
            service_ids: Collection[int],
            service_ids_prev_active: Collection[int],
    ) -> List[contracts.Contract]:
        return self._items


class Tariffs(tariffs.Repository):
    def __init__(self, data: List[dict]):
        self._categories = {
            category['id']: self._parse_category(category)
            for tariff in data
            for category in tariff['categories']
        }

        self._tariff_zones = {
            tariff_zone['name']: self._parse_tariff_zone(tariff_zone)
            for tariff in data
            for tariff_zone in tariff['tariff_zones']
        }

    async def fetch_category_by_id(self, category_id) -> tariffs.Category:
        category = self._categories.get(category_id)
        if category:
            return category
        raise tariffs.CategoryNotFoundError(
            f'Category {category_id} not found',
        )

    async def fetch_tariff_zone_by_name(
            self, zone_name: str,
    ) -> taxi_tariffs_models.TariffZonesItem:

        tariff_zone = self._tariff_zones.get(zone_name)
        if tariff_zone:
            return tariff_zone
        raise tariffs.TariffZoneNotFoundError(f'Zone {zone_name} not found')

    @staticmethod
    def _parse_category(category_data: Dict[str, Any]) -> tariffs.Category:
        return tariffs.Category(
            minimal_cost=billing.Money(
                decimal.Decimal(category_data['minimal']['amount']),
                category_data['minimal']['currency'],
            ),
            name=category_data['name'],
        )

    @staticmethod
    def _parse_tariff_zone(
            tariff_zone: Dict[str, Any],
    ) -> taxi_tariffs_models.TariffZonesItem:
        return taxi_tariffs_models.TariffZonesItem(**tariff_zone)


class CurrencyRates(currency_rates.Repository):
    def __init__(self, data: Dict[_CurrencyPair, Dict[_Date, _Decimal]]):
        self._data = {
            key: self._parse_rate_history(value) for key, value in data.items()
        }

    async def fetch(
            self, from_currency: str, to_currency: str, on_date: dt.date,
    ) -> decimal.Decimal:
        if from_currency == to_currency:
            return decimal.Decimal('1')
        rate_history = self._data.get(from_currency + to_currency)
        if rate_history:
            rate = rate_history.get(on_date)
            if rate:
                return rate
        raise currency_rates.CurrencyRateNotFoundError(
            f'Rate {from_currency}-{to_currency} '
            f'for date {on_date} not found',
        )

    @staticmethod
    def _parse_rate_history(
            data: Dict[_Date, _Decimal],
    ) -> Dict[dt.date, decimal.Decimal]:
        return {
            dates.parse_date(key): decimal.Decimal(value)
            for key, value in data.items()
        }


class DriverModeSettings(driver_mode_settings.Repository):
    def __init__(self, tags: List[str]):
        self._tags = tags

    def fetch_tags(self, mode_rule: str, as_of: dt.datetime) -> List[str]:
        return self._tags


class Subscriptions(driver_mode_subscriptions.Repository):
    def __init__(self, doc: Optional[driver_mode_subscriptions.Doc]):
        self._subs_doc = doc

    async def fetch(
            self, park_id: str, driver_profile_id: str, as_of: dt.datetime,
    ) -> Optional[driver_mode_subscriptions.Doc]:
        return self._subs_doc


class CommissionAgreements(commission_agreements.Repository):
    def __init__(self, agreements: List[commission_agreements.Agreement]):
        self._agreements = agreements

    async def match(
            self,
            query: Union[
                commission_agreements.Query, commission_agreements.FineQuery,
            ],
    ) -> List[commission_agreements.Agreement]:
        return self._agreements

    async def match_fine_agreement(
            self, query: commission_agreements.FineQuery,
    ) -> commission_agreements.Agreement:
        agreements = await self.match(query)
        return self._fetch_fine_agreement(agreements)

    def _fetch_fine_agreement(
            self, agreements: List[commission_agreements.Agreement],
    ) -> commission_agreements.Agreement:
        fine_agreements = (
            agr
            for agr in agreements
            if agr.group == consts.CommissionGroup.FINE
        )
        return more_itertools.one(
            fine_agreements,
            too_long=ValueError('Ambiguous fine commission agreement'),
        )


class Antifraud(antifraud.Repository):
    def __init__(self, allow: bool):
        self._allow = allow

    @staticmethod
    def always_allowing() -> Antifraud:
        return Antifraud(allow=True)

    async def check_order(
            self,
            order_id: str,
            transporting_distance_meters: int,
            transporting_time_seconds: int,
            use_bulk_af: bool,
            goal_precheck_enabled: bool,
    ) -> antifraud.CheckOrderResult:
        if use_bulk_af:
            return antifraud.CheckOrderResult(
                is_single_ride_allowed=self._allow,
                is_single_on_top_allowed=self._allow,
                is_goal_allowed=self._allow if goal_precheck_enabled else True,
            )
        return antifraud.CheckOrderResult(
            is_single_ride_allowed=self._allow,
            is_single_on_top_allowed=self._allow,
            is_goal_allowed=True,
        )


class DriverFixRules(driver_fix_rules.Repository):
    def __init__(self, rule: driver_fix_rules.Rule):
        self._rule = rule

    async def fetch(
            self, reference_rule_id: str, as_of: dt.datetime, time_zone: str,
    ) -> driver_fix_rules.Rule:
        assert (
            reference_rule_id == self._rule.id
        ), f'{reference_rule_id} != {self._rule.id}'
        return self._rule


class SupportInfo(support_info.Repository):
    def __init__(self):
        self.queries: List[dict] = []

    async def save_for_driver_mode(
            self,
            data: support_info.DriverModeData,
            alias_id: str,
            doc_id: int,
            is_testing_migration_mode: bool,
    ) -> Optional[int]:
        self._save_query(data, doc_id, alias_id)
        return self._gen_doc_id()

    async def save_for_commission(
            self,
            data: support_info.CommissionData,
            doc_id: int,
            alias_id: str,
            is_testing_migration_mode: bool,
    ) -> Optional[int]:
        self._save_query(data, doc_id, alias_id)
        return self._gen_doc_id()

    async def save_for_fine(
            self,
            data: support_info.CommissionData,
            doc_id: int,
            alias_id: str,
            is_testing_migration_mode: bool,
    ) -> Optional[int]:
        self._save_query(data, doc_id, alias_id)
        return self._gen_doc_id()

    async def save_for_order_subvention(
            self,
            data: support_info.OrderSubventionData,
            doc_id: int,
            alias_id: str,
            is_testing_migration_mode: bool,
    ) -> Optional[int]:
        self._save_query(data, doc_id, alias_id)
        return self._gen_doc_id()

    def _save_query(
            self,
            data: Union[
                support_info.CommissionData,
                support_info.DriverModeData,
                support_info.OrderSubventionData,
            ],
            doc_id: int,
            alias_id: str,
    ):
        self.queries.append(
            {'data': data.serialize(), 'alias_id': alias_id, 'doc_id': doc_id},
        )

    def _gen_doc_id(self) -> int:
        return len(self.queries) + 1000
