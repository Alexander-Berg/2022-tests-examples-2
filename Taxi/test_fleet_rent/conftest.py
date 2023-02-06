# pylint: disable=redefined-outer-name
import datetime
import typing

import pytest

from taxi import pro_app

from fleet_rent.entities import driver
from fleet_rent.entities import park
import fleet_rent.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['fleet_rent.generated.service.pytest_plugins']


@pytest.fixture
def driver_auth_headers(dap_headers_factory) -> typing.Dict[str, str]:
    return dap_headers_factory(
        park_id='driver_park_id',
        driver_id='driver_id',
        pro_app=pro_app.ProApp(
            version=pro_app.AppVersion(9, 10, 0),
            version_type=pro_app.VersionType.PRODUCTION,
            platform=pro_app.Platform.ANDROID,
            brand=pro_app.Brand.YANDEX,
            build_type=pro_app.BuildType.DEFAULT,
            platform_version=pro_app.PlatformVersion(15, 14, 13),
        ),
    )


@pytest.fixture
def park_stub_factory():
    # noinspection PyShadowingBuiltins
    def factory(  # pylint: disable=invalid-name
            id: str = 'id',  # pylint: disable=redefined-builtin
            name: typing.Optional[str] = 'ИмяПарка',
            clid: typing.Optional[str] = '100500',
            owner: typing.Optional[str] = 'owner',
            tz_offset: typing.Optional[int] = 3,
            city_id: typing.Optional[str] = 'Москва',
            country_id: typing.Optional[str] = 'rus',
            fleet_type: typing.Optional[str] = 'yandex',
            locale: typing.Optional[str] = 'ru',
            driver_partner_source: typing.Optional[str] = None,
    ):
        if id.startswith('bad_id'):
            # "bad" park - exists, but has no info in other sources
            return park.Park(id=id)
        return park.Park(
            id=id,
            name=name,
            clid=clid,
            owner=owner,
            tz_offset=tz_offset,
            city_id=city_id,
            country_id=country_id,
            fleet_type=fleet_type,
            locale=locale,
            driver_partner_source=driver_partner_source,
        )

    return factory


@pytest.fixture
def park_billing_data_stub_factory():
    def factory(
            clid: typing.Optional[str] = 'clid',
            inn: typing.Optional[str] = 'inn',
            billing_client_id: typing.Optional[str] = 'billing_client_id',
            legal_address: typing.Optional[str] = 'legal_address',
            legal_name: typing.Optional[str] = 'legal_name',
    ):
        return park.ParkBillingClientData(
            clid=clid,
            inn=inn,
            billing_client_id=billing_client_id,
            legal_address=legal_address,
            legal_name=legal_name,
        )

    return factory


@pytest.fixture
def park_contacts_stub_factory():
    # noinspection PyShadowingBuiltins
    def factory(  # pylint: disable=invalid-name
            id: str = 'id',  # pylint: disable=redefined-builtin
            phone: typing.Optional[str] = 'phone',
            address: typing.Optional[str] = 'address',
            lon: typing.Optional[str] = 'lon',
            lat: typing.Optional[str] = 'lat',
    ):
        coordinates = None
        if lon and lat:
            coordinates = park.ParkCoordinates(lon, lat)
        return park.ParkContacts(
            id=id, phone=phone, address=address, coordinates=coordinates,
        )

    return factory


@pytest.fixture
def mock_load_park_contacts(patch, park_contacts_stub_factory):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_contacts')
    async def _get(park_id: str):
        return park_contacts_stub_factory(id=park_id)


@pytest.fixture
def mock_load_park_info(patch, park_stub_factory, mock_load_billing_data):
    @patch(
        'fleet_rent.services.park_info.ParkInfoService'
        '._get_park_info_batch_direct',
    )
    async def _get_basic(park_ids: typing.AbstractSet[str]):
        res = {}
        for park_id in park_ids:
            driver_partner_source = None
            if park_id.startswith('driver'):
                driver_partner_source = 'self_assign'
            res[park_id] = park_stub_factory(
                park_id, driver_partner_source=driver_partner_source,
            )
        return res


@pytest.fixture
def mock_load_billing_data(patch, park_billing_data_stub_factory):
    @patch(
        'fleet_rent.services.park_info.ParkInfoService.get_park_billing_data',
    )
    async def _get_billing_data(clid: typing.Optional[str]):
        if not clid:
            inn = None
            client_id = None
            legal_address = None
            legal_name = None
        else:
            inn = 'inn'
            client_id = 'billing_client_id'
            legal_address = 'legal_address'
            legal_name = 'legal_name'
        return park_billing_data_stub_factory(
            clid=clid,
            inn=inn,
            billing_client_id=client_id,
            legal_address=legal_address,
            legal_name=legal_name,
        )


@pytest.fixture
def park_branding_yandex():
    return park.Branding(
        id=park.ParkBrand.YANDEX,
        control_email='no-reply@taxi.yandex.com',
        main_page='https://driver.yandex',
        no_reply_email='no-reply@taxi.yandex.com',
        opteum_external_uri='https://opteum.taxi.tst.yandex.ru',
        opteum_support_uri='https://opteum.taxi.tst.yandex-team.ru',
        park_support_email='park@taxi.yandex.com',
        support_page='https://taxi.taxi.tst.yandex.ru/taximeter-info',
        support_page_driver_partner='https://техподдержка-таксопарков',
    )


@pytest.fixture
def mock_load_park_branding(patch, park_branding_yandex):
    @patch('fleet_rent.services.confing3.Configs3Service.get_park_branding')
    async def _get(park_info: park.Park):
        return park_branding_yandex


@pytest.fixture
def driver_stub_factory():
    def make(park_id: str, driver_id: str):
        if driver_id.startswith('bad'):
            # "bad" driver - exists, but has no info in other sources
            return driver.Driver(id=driver_id, park_id=park_id, full_name=None)
        return driver.Driver(
            id=driver_id,
            park_id=park_id,
            full_name=driver.Driver.FullName(
                first_name='Водитель',
                last_name='Водителев',
                middle_name='Водителевич',
            ),
        )

    return make


@pytest.fixture
def mock_load_driver_info(patch, driver_stub_factory):
    @patch('fleet_rent.services.driver_info.DriverInfoService.get_driver_info')
    async def _get(park_id: str, driver_id: str):
        return driver_stub_factory(park_id, driver_id)


@pytest.fixture
def driver_app_stub_factory():
    def make(park_id: str, driver_id: str):
        if driver_id.startswith('bad'):
            # "bad" driver - exists, but has no info in other sources
            return driver.DriverApp(id=driver_id, park_id=park_id, locale=None)
        return driver.DriverApp(id=driver_id, park_id=park_id, locale='ru')

    return make


@pytest.fixture
def mock_load_driver_app_info(patch, driver_app_stub_factory):
    @patch('fleet_rent.services.driver_info.DriverInfoService.get_app')
    async def _get(park_id: str, driver_id: str):
        return driver_app_stub_factory(park_id, driver_id)


@pytest.fixture
def park_user_stub_factory():
    from fleet_rent.entities import park_user

    # noinspection PyShadowingBuiltins
    def factory(  # pylint: disable=invalid-name
            id: str = 'id',  # pylint: disable=redefined-builtin
            park_id: str = 'park_id',
            name: typing.Optional[str] = 'park-director',
            email: typing.Optional[str] = 'park-director@yandex.ru',
            is_superuser: bool = True,
    ) -> park_user.ParkUser:
        return park_user.ParkUser(
            id=id,
            park_id=park_id,
            name=name,
            email=email,
            is_superuser=is_superuser,
        )

    return factory


@pytest.fixture
def billing_contract_stub_factory():
    from fleet_rent.entities import billing

    # noinspection PyShadowingBuiltins
    def factory(  # pylint: disable=invalid-name
            id: int = 1,  # pylint: disable=redefined-builtin
            currency: str = 'RUB',
    ) -> billing.Contract:
        return billing.Contract(id=id, currency=currency)

    return factory


@pytest.fixture
def mock_load_billing_contract(patch, billing_contract_stub_factory):
    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.get_park_contract',
    )
    async def _get(park_info: park.Park, actual_at: datetime.datetime):
        return billing_contract_stub_factory()


@pytest.fixture
def mock_find_park_owner(patch, park_user_stub_factory):
    @patch('fleet_rent.services.park_users.ParkUsersService.find_park_owner')
    async def _find(park_id: str):
        return park_user_stub_factory(park_id)


@pytest.fixture
def rent_stub_factory():
    from fleet_rent.entities import rent

    _stub_dt = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)

    def factory(
            record_id: str = 'record_id',
            owner_park_id: str = 'park_id',
            owner_serial_id: int = 1,
            driver_id: str = 'driver_id',
            affiliation_id: typing.Optional[str] = None,
            title: typing.Optional[str] = None,
            comment: typing.Optional[str] = None,
            balance_notify_limit: typing.Optional[str] = None,
            begins_at: datetime.datetime = _stub_dt,
            ends_at: typing.Optional[datetime.datetime] = None,
            asset: rent.asset.Asset = rent.asset.AssetOther(
                subtype='misc', description=None,
            ),
            charging: rent.charging.Charging = rent.charging.ChargingFree(
                starts_at=_stub_dt, finishes_at=None,
            ),
            charging_starts_at: datetime.datetime = _stub_dt,
            creator_uid: str = 'creator_uid',
            created_at: datetime.datetime = _stub_dt,
            accepted_at: typing.Optional[datetime.datetime] = None,
            acceptance_reason: typing.Optional[str] = None,
            rejected_at: typing.Optional[datetime.datetime] = None,
            rejection_reason: typing.Optional[str] = None,
            terminated_at: typing.Optional[datetime.datetime] = None,
            termination_reason: typing.Optional[str] = None,
            last_seen_at: typing.Optional[datetime.datetime] = None,
            use_billing_order_id_fix: bool = False,
            use_event_queue: bool = False,
            use_arbitrary_entries: bool = False,
            start_clid=None,
    ):
        if use_billing_order_id_fix:
            ton = f'{owner_park_id}_{owner_serial_id}'
        else:
            ton = str(owner_serial_id)
        return rent.Rent(
            record_id=record_id,
            owner_park_id=owner_park_id,
            owner_serial_id=owner_serial_id,
            driver_id=driver_id,
            affiliation_id=affiliation_id,
            title=title,
            comment=comment,
            balance_notify_limit=balance_notify_limit,
            begins_at=begins_at,
            ends_at=ends_at,
            asset=asset,
            charging=charging,
            charging_starts_at=charging_starts_at,
            creator_uid=creator_uid,
            created_at=created_at,
            accepted_at=accepted_at,
            acceptance_reason=acceptance_reason,
            rejected_at=rejected_at,
            rejection_reason=rejection_reason,
            terminated_at=terminated_at,
            termination_reason=termination_reason,
            last_seen_at=last_seen_at,
            transfer_order_number=ton,
            use_event_queue=use_event_queue,
            use_arbitrary_entries=use_arbitrary_entries,
            start_clid=start_clid,
        )

    return factory


@pytest.fixture
def aff_stub_factory():
    from fleet_rent.entities import affiliation

    _stub_dt = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)

    def factory(
            record_id: str = 'affiliation_id',
            park_id: str = 'park_id',
            local_driver_id: str = 'driver_id',
            original_driver_park_id: str = 'OriginalDriverParkId',
            original_driver_id: str = 'OriginalDriverId',
            state: affiliation.AffiliationState = affiliation.ACTIVE_STATE,
            creator_uid: str = 'creator_uid',
            created_at: datetime.datetime = _stub_dt,
            modified_at: datetime.datetime = _stub_dt,
    ):
        return affiliation.Affiliation(
            record_id=record_id,
            park_id=park_id,
            local_driver_id=local_driver_id,
            original_driver_park_id=original_driver_park_id,
            original_driver_id=original_driver_id,
            state=state,
            creator_uid=creator_uid,
            created_at_tz=created_at,
            modified_at_tz=modified_at,
        )

    return factory


@pytest.fixture
def car_stub_factory():
    from fleet_rent.entities import car

    # noinspection PyShadowingBuiltins
    def factory(  # pylint: disable=invalid-name
            park_id: str = 'park_id',
            id: str = 'car_id',  # pylint: disable=redefined-builtin
            model: typing.Optional[str] = 'model',
            brand: typing.Optional[str] = 'brand',
            number: typing.Optional[str] = 'number',
            color: typing.Optional[str] = 'color',
            year: typing.Optional[int] = 2525,
    ) -> car.Car:
        return car.Car(
            park_id=park_id,
            id=id,
            model=model,
            brand=brand,
            number=number,
            color=color,
            year=year,
        )

    return factory


@pytest.fixture
def mock_load_car_info(patch, car_stub_factory):
    @patch('fleet_rent.services.car_info.CarInfoService.get_car_info')
    async def _get(park_id: str, car_id: str):
        return car_stub_factory(park_id, car_id)
