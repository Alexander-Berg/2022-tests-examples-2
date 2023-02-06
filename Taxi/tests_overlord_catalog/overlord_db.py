import dataclasses

from . import sql_queries
from .plugins import mock_personal


DEFAULT_TIMETABLE = ['00:00', '24:00']
DEFAULT_IN_STOCK = 1
DEFAULT_DEPLETED = '2020-01-01 00:00:00.000000+00'
DEFAULT_RESTORED = '2020-01-01 00:00:00.000000+00'
DEFAULT_PRICE = 100500
DEFAULT_AMOUNT = 5.0000
DEFAULT_AMOUNT_UNIT = 'kg'
DEFAULT_UPDATED = '2020-07-07T00:00:00+00:00'

DEPOT_ID_TEMPLATE = '0123456789abcdef{:028d}'
CATEGORY_ID_TEMPLATE = '01234567-89ab-cdef-000a-{:06d}{:06d}'
ASSORTMENT_ID_TEMPLATE = '01234567-89ab-cdef-000b-{:06d}000000'
ASSORTMENT_ITEM_ID_TEMPLATE = '9876543-21ab-cdef-000b-{:06d}{:06d}'
PRICE_LIST_ID_TEMPLATE = '01234567-89ab-cdef-000c-{:06d}000000'
PRICE_LIST_ITEM_ID_TEMPLATE = 'abcdef9-8976-4321-000b-{:06d}{:06d}'
PRODUCT_ID_TEMPLATE = '01234567-89ab-cdef-0000-{:012d}'

ZONE_BASE_LON = 37.29
ZONE_BASE_LAT = 55.91
ZONE_SIZE = 0.01
ZONE_STEP = 0.05

NONE_EATS_ID = 99999999


def _execute_sql_query(sql_query, pgsql):
    db = pgsql['overlord_catalog']
    cursor = db.cursor()
    cursor.execute(sql_query)


def _generate_location_and_zone(seed):
    seed = seed - 1

    left_up_angle_lon = ZONE_BASE_LON + ZONE_STEP * int(seed % 10)
    left_up_angle_lat = ZONE_BASE_LAT - ZONE_STEP * int(seed / 10)

    right_up_angle_lon = left_up_angle_lon + ZONE_SIZE
    right_up_angle_lat = left_up_angle_lat

    right_down_angle_lon = right_up_angle_lon
    right_down_angle_lat = right_up_angle_lat - ZONE_SIZE

    left_down_angle_lon = left_up_angle_lon
    left_down_angle_lat = right_down_angle_lat

    location_lon = (
        left_up_angle_lon
        + right_up_angle_lon
        + right_down_angle_lon
        + left_down_angle_lon
    ) / 4

    location_lat = (
        left_up_angle_lat
        + right_up_angle_lat
        + right_down_angle_lat
        + left_down_angle_lat
    ) / 4

    location = [location_lon, location_lat]
    zone = {
        'type': 'MultiPolygon',
        'coordinates': [
            [
                [
                    [left_up_angle_lon, left_up_angle_lat],
                    [right_up_angle_lon, right_up_angle_lat],
                    [right_down_angle_lon, right_down_angle_lat],
                    [left_down_angle_lon, left_down_angle_lat],
                    [left_up_angle_lon, left_up_angle_lat],
                ],
            ],
        ],
    }

    return location, zone


def _generate_eats_id(seed):
    return 1000 + seed


class OverlordDbAgent:
    def __init__(self, pgsql):
        self._pgsql = pgsql
        self._in_transaction = False
        self._sql_query = ''

        self._depots = {}

    def begin_transaction(self):
        assert not self._in_transaction
        self._in_transaction = True

    def commit_transaction(self):
        assert self._in_transaction

        sql_query = sql_queries.transaction(self._sql_query)
        _execute_sql_query(sql_query, pgsql=self._pgsql)

        self._sql_query = ''
        self._in_transaction = False

    def refresh_wms_views(self):
        self.apply_sql_query(
            sql_queries.refresh_wms_views(), as_transaction=True,
        )

    def __enter__(self):
        self.begin_transaction()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is None:
            self.refresh_wms_views()
            self.commit_transaction()

    def add_company(self, company_id: str):
        company = Company(company_id=company_id)
        company.insert(overlord_db_agent=self)
        return company

    def add_depot(
            self,
            depot_id,
            location=None,
            zone=None,
            timetable=None,
            allow_parcels=False,
            region_id=None,
            currency=None,
            time_range=None,
            company_id=None,
            open_ts=None,
            timezone=None,
            country_iso3='RUS',
            country_iso2='RU',
            root_category_external_id=None,
    ):
        assert (
            isinstance(depot_id, int)
            and depot_id > 0
            and depot_id not in self._depots
        )

        depot = Depot(
            depot_id=depot_id,
            overlord_db_agent=self,
            location=location,
            zone=zone,
            timetable=timetable,
            allow_parcels=allow_parcels,
            region_id=region_id,
            currency=currency,
            time_range=time_range,
            company_id=company_id,
            open_ts=open_ts,
            timezone=timezone,
            country_iso3=country_iso3,
            country_iso2=country_iso2,
            root_category_external_id=root_category_external_id,
        )

        self._depots[depot_id] = depot

        return depot

    def get_depot(self, depot_id):
        return self._depots[depot_id]

    def has_product(self, product_id):
        for depots in self._depots.values():
            if depots.has_product(product_id):
                return True
        return False

    def apply_sql_query(self, sql_query, as_transaction=False):
        if self._in_transaction:
            self._sql_query += f'\n{sql_query}'
        else:
            if as_transaction:
                sql_query = sql_queries.transaction(sql_query)
            _execute_sql_query(sql_query, pgsql=self._pgsql)


@dataclasses.dataclass
class Company:
    company_id: str
    external_id: str = 'company-external-id'
    title: str = 'company-title'
    tin: str = mock_personal.DEFAULT_TIN

    def insert(self, overlord_db_agent):
        add_company_query = sql_queries.add_company(
            self.company_id, self.external_id, self.title, self.tin,
        )

        overlord_db_agent.apply_sql_query(
            add_company_query, as_transaction=True,
        )


class Depot:
    def __init__(
            self,
            depot_id,
            overlord_db_agent,
            location=None,
            zone=None,
            timetable=None,
            allow_parcels=False,
            region_id=None,
            currency='RUB',
            time_range=None,
            company_id='some-company-id',
            open_ts=None,
            timezone=None,
            country_iso3='RUS',
            country_iso2='RU',
            root_category_external_id=None,
    ):
        if location is None and zone is None:
            location, zone = _generate_location_and_zone(depot_id)

        if region_id is None:
            region_id = 213

        if time_range is None:
            time_range = ('00:00', '24:00')

        if timezone is None:
            timezone = 'Europe/Moscow'

        assert location is not None and zone is not None

        self._region_id = region_id
        self._depot_id = depot_id
        self._id_wms = DEPOT_ID_TEMPLATE.format(depot_id)
        self._overlord_db_agent = overlord_db_agent
        self._location = location
        self._zone = zone
        self._assortment_id = ASSORTMENT_ID_TEMPLATE.format(depot_id)
        self._price_list_id = PRICE_LIST_ID_TEMPLATE.format(depot_id)
        self._allow_parcels = allow_parcels
        self._open_ts = open_ts
        self._timezone = timezone
        self._currency = currency
        self._country_iso3 = country_iso3
        self._country_iso2 = country_iso2

        root_category_id = 0
        root_category = Category(
            category_id=root_category_id,
            external_id=root_category_external_id,
            depot=self,
            overlord_db_agent=overlord_db_agent,
            rank=1000 * depot_id,
            timetable=timetable,
            eats_id=1000 * depot_id,
        )

        self._categories = {root_category_id: root_category}
        self._root_category = root_category

        add_depot_query = sql_queries.add_depot(
            depot_id=self._id_wms,
            external_id=depot_id,
            location=location,
            zone=zone,
            root_category_id=root_category.id_wms,
            assortment_id=self._assortment_id,
            price_list_id=self._price_list_id,
            allow_parcels=allow_parcels,
            region_id=region_id,
            currency=currency,
            time_range=time_range,
            company_id=company_id,
            open_ts=open_ts,
            timezone=timezone,
        )

        overlord_db_agent.apply_sql_query(add_depot_query, as_transaction=True)

    @property
    def currency(self):
        return self._currency

    @property
    def timezone(self):
        return self._timezone

    @property
    def allow_parcels(self):
        return self._allow_parcels

    @property
    def depot_id(self):
        return self._depot_id

    @property
    def region_id(self):
        return self._region_id

    @property
    def id_wms(self):
        return self._id_wms

    @property
    def location(self):
        return self._location

    @property
    def zone(self):
        return self._zone

    @property
    def assortment_id(self):
        return self._assortment_id

    @property
    def price_list_id(self):
        return self._price_list_id

    @property
    def root_category(self):
        return self._root_category

    @property
    def country_iso2(self):
        return self._country_iso2

    @property
    def country_iso3(self):
        return self._country_iso3

    def add_category(
            self,
            category_id,
            external_id=None,
            timetable=None,
            parent_id=None,
            eats_id=None,
            status=None,
    ):
        if parent_id is None:
            parent = self._root_category
        else:
            parent = self._categories[parent_id]

        assert (
            isinstance(category_id, int)
            and category_id > 0
            and category_id not in self._categories
        )

        category = Category(
            category_id=category_id,
            depot=self,
            overlord_db_agent=self._overlord_db_agent,
            rank=self._root_category.rank + category_id,
            timetable=timetable,
            parent_id=parent.id_wms,
            eats_id=eats_id,
            status=status,
            external_id=external_id,
        )

        self._categories[category_id] = category

        return category

    def get_category(self, category_id):
        return self._categories[category_id]

    def add_product(
            self,
            product_id,
            status=None,
            in_stock=None,
            depleted=None,
            restored=None,
            price=None,
            checkout_limit=None,
            eats_id=None,
            vat='20.00',
            updated=None,
            country=None,
            country_of_origin=None,
            shelf_type='store',
    ):
        return self._root_category.add_product(
            product_id=product_id,
            status=status,
            in_stock=in_stock,
            depleted=depleted,
            restored=restored,
            price=price,
            checkout_limit=checkout_limit,
            eats_id=eats_id,
            vat=vat,
            updated=updated,
            country=country,
            country_of_origin=country_of_origin,
            shelf_type=shelf_type,
        )

    def get_product(self, product_id):
        for category in self._categories.values():
            if category.has_product(product_id):
                return category.get_product(product_id)
        assert False
        return None

    def has_product(self, product_id):
        for category in self._categories.values():
            if category.has_product(product_id):
                return True
        return False


class Category:
    def __init__(
            self,
            category_id,
            depot,
            overlord_db_agent,
            rank,
            timetable=None,
            parent_id=None,
            eats_id=None,
            status=None,
            external_id=None,
    ):
        if timetable is None:
            timetable = DEFAULT_TIMETABLE

        self._eats_id = eats_id
        if eats_id is None:
            self._eats_id = _generate_eats_id(category_id)

        if eats_id == NONE_EATS_ID:
            self._eats_id = None

        self._id_wms = CATEGORY_ID_TEMPLATE.format(depot.depot_id, category_id)
        self._depot = depot
        self._overlord_db_agent = overlord_db_agent
        self._rank = rank
        self._status = status

        self._products = {}

        add_category_query = sql_queries.add_category(
            category_id=self._id_wms,
            external_id=external_id,
            rank=rank,
            timetable=timetable,
            parent_id=parent_id,
            external_depot_id=depot.depot_id,
            eats_id=self._eats_id,
            status=self._status,
        )

        overlord_db_agent.apply_sql_query(add_category_query)

    @property
    def id_wms(self):
        return self._id_wms

    @property
    def rank(self):
        return self._rank

    @property
    def eats_id(self):
        return self._eats_id

    @property
    def status(self):
        return self._status

    def add_product(
            self,
            product_id,
            external_id=None,
            status=None,
            in_stock=None,
            depleted=None,
            restored=None,
            price=None,
            checkout_limit=None,
            eats_id=None,
            vat='20.00',
            updated=None,
            country=None,
            country_of_origin=None,
            amount_unit=None,
            amount_unit_alias=None,
            manufacturer=None,
            amount=None,
            storage_traits=None,
            ingredients=None,
            shelf_type='store',
            measurements=None,
            grades=None,
            parent_id=None,
            barcodes=None,
            important_ingredients=None,
            main_allergens=None,
            photo_stickers=None,
            custom_tags=None,
            logistic_tags=None,
            set_default_stock=True,
            supplier_tin=None,
    ):
        assert isinstance(product_id, int) and product_id > 0

        product = Product(
            product_id=product_id,
            category=self,
            depot=self._depot,
            overlord_db_agent=self._overlord_db_agent,
            external_id=external_id,
            status=status,
            in_stock=in_stock,
            depleted=depleted,
            restored=restored,
            price=price,
            checkout_limit=checkout_limit,
            eats_id=eats_id,
            vat=vat,
            updated=updated,
            country=country,
            country_of_origin=country_of_origin,
            amount_unit=amount_unit,
            amount_unit_alias=amount_unit_alias,
            manufacturer=manufacturer,
            amount=amount,
            storage_traits=storage_traits,
            ingredients=ingredients,
            shelf_type=shelf_type,
            measurements=measurements,
            grades=grades,
            parent_id=parent_id,
            barcodes=barcodes,
            important_ingredients=important_ingredients,
            main_allergens=main_allergens,
            photo_stickers=photo_stickers,
            custom_tags=custom_tags,
            logistic_tags=logistic_tags,
            set_default_stock=set_default_stock,
            supplier_tin=supplier_tin,
        )

        self._products[product_id] = product

        return product

    def get_product(self, product_id):
        return self._products[product_id]

    def has_product(self, product_id):
        return product_id in self._products


class Product:
    def __init__(
            self,
            product_id,
            category,
            depot,
            overlord_db_agent,
            status=None,
            external_id=None,
            in_stock=None,
            depleted=None,
            restored=None,
            price=None,
            checkout_limit=None,
            eats_id=None,
            vat='20.00',
            updated=None,
            country=None,
            country_of_origin=None,
            amount_unit=None,
            amount_unit_alias=None,
            manufacturer=None,
            amount=None,
            storage_traits=None,
            ingredients=None,
            shelf_type='store',
            measurements=None,
            grades=None,
            parent_id=None,
            barcodes=None,
            important_ingredients=None,
            main_allergens=None,
            photo_stickers=None,
            custom_tags=None,
            logistic_tags=None,
            set_default_stock=True,
            supplier_tin=None,
    ):
        if external_id is None:
            external_id = product_id
        if status is None:
            status = 'active'
        if in_stock is None and set_default_stock:
            in_stock = DEFAULT_IN_STOCK
        if depleted is None:
            depleted = DEFAULT_DEPLETED
        if restored is None:
            restored = DEFAULT_RESTORED
        if price is None:
            price = DEFAULT_PRICE
        if updated is None:
            updated = DEFAULT_UPDATED

        if eats_id is None:
            eats_id = _generate_eats_id(product_id)
        if eats_id == NONE_EATS_ID:
            eats_id = None

        if amount_unit is None:
            amount_unit = DEFAULT_AMOUNT_UNIT
        if amount is None:
            amount = DEFAULT_AMOUNT

        self._id_wms = PRODUCT_ID_TEMPLATE.format(product_id)
        self._external_id = external_id
        self._status = status
        self._in_stock = in_stock
        self._depleted = depleted
        self._restored = restored
        self._price = price
        self._checkout_limit = checkout_limit
        self._vat = vat
        self._updated = updated
        self._country = country
        self._country_of_origin = country_of_origin
        self._amount_unit = amount_unit
        self._amount_unit_alias = amount_unit_alias
        self._manufacturer = manufacturer

        self._amount = amount
        self._storage_traits = storage_traits
        self._rank = product_id
        self._ranks = [product_id]
        self._measurements = measurements

        self._grades = grades
        self._parent_id = parent_id
        self._barcodes = barcodes
        self._important_ingredients = important_ingredients
        self._main_allergens = main_allergens
        self._photo_stickers = photo_stickers
        self._custom_tags = custom_tags
        self._logistic_tags = logistic_tags
        self._supplier_tin = supplier_tin

        add_to_products = not overlord_db_agent.has_product(product_id)
        add_to_depot = not depot.has_product(product_id)
        add_to_category = not category.has_product(product_id)

        assert add_to_products or add_to_depot or add_to_category

        if not add_to_depot:
            product = depot.get_product(product_id)
            assert (
                in_stock == product.in_stock
                and depleted == product.depleted
                and price == product.price
            )

        assortment_item_id = ASSORTMENT_ITEM_ID_TEMPLATE.format(
            depot.depot_id, product_id,
        )
        price_list_item_id = PRICE_LIST_ITEM_ID_TEMPLATE.format(
            depot.depot_id, product_id,
        )

        add_product_query = sql_queries.add_product(
            product_id=self._id_wms,
            external_id=self._external_id,
            status=self._status,
            rank=self._rank,
            ranks=self._ranks,
            in_stock=in_stock,
            depleted=depleted,
            restored=restored,
            price=price,
            depot_id=depot.id_wms,
            external_depot_id=depot.depot_id,
            category_id=category.id_wms,
            assortment_id=depot.assortment_id,
            assortment_item_id=assortment_item_id,
            price_list_id=depot.price_list_id,
            price_list_item_id=price_list_item_id,
            add_to_products=add_to_products,
            add_to_depot=add_to_depot,
            add_to_category=add_to_category,
            checkout_limit=checkout_limit,
            eats_id=eats_id,
            vat=vat,
            updated=updated,
            country=country,
            country_of_origin=country_of_origin,
            amount_unit=amount_unit,
            amount_unit_alias=amount_unit_alias,
            manufacturer=manufacturer,
            amount=amount,
            storage_traits=storage_traits,
            ingredients=ingredients,
            shelf_type=shelf_type,
            measurements=measurements,
            grades=grades,
            parent_id=parent_id,
            barcodes=barcodes,
            important_ingredients=important_ingredients,
            main_allergens=main_allergens,
            photo_stickers=photo_stickers,
            custom_tags=custom_tags,
            logistic_tags=logistic_tags,
            supplier_tin=supplier_tin,
        )

        overlord_db_agent.apply_sql_query(
            add_product_query, as_transaction=True,
        )

    @property
    def id_wms(self):
        return self._id_wms

    @property
    def status(self):
        return self._status

    @property
    def in_stock(self):
        return self._in_stock

    @property
    def depleted(self):
        return self._depleted

    @property
    def price(self):
        return self._price

    @property
    def checkout_limit(self):
        return self._checkout_limit

    @property
    def vat(self):
        return self._vat

    @property
    def updated(self):
        return self._updated

    @property
    def amount_unit(self):
        return self._amount_unit

    @property
    def amount_unit_alias(self):
        return self._amount_unit_alias

    @property
    def amount(self):
        return self._amount

    @property
    def rank(self):
        return self._rank

    @property
    def ranks(self):
        return self._ranks

    @property
    def barcodes(self):
        return self._barcodes

    @property
    def important_ingredients(self):
        return self._important_ingredients

    @property
    def main_allergens(self):
        return self._main_allergens

    @property
    def photo_stickers(self):
        return self._photo_stickers

    @property
    def custom_tags(self):
        return self._custom_tags

    @property
    def logistic_tags(self):
        return self._logistic_tags

    @property
    def supplier_tin(self):
        return self._supplier_tin
