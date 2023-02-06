# pylint: disable=redefined-outer-name,unused-variable,protected-access
import pytest

from testsuite.utils import http

from selfemployed.generated.web import web_context
from selfemployed.helpers import actions


@pytest.mark.parametrize(
    'license_data',
    [
        {
            'license': {
                'number': '1111 000000',
                'normalized_number': '1111000000',
                'expiration_date': 'exp_date',
                'issue_date': 'iss_date',
            },
            'license_number': '000000',
            'license_series': '1111',
        },
        {
            'license': {
                'number': '1111000000',
                'normalized_number': '1111000000',
                'expiration_date': 'exp_date',
                'issue_date': 'iss_date',
            },
        },
        {
            'license': {
                'number': '1111 000000',
                'normalized_number': '1111000000',
                'expiration_date': 'exp_date',
                'issue_date': 'iss_date',
            },
        },
    ],
)
@pytest.mark.parametrize(
    'yet_another_driver_info',
    [
        {'delivery': {'thermobag': True, 'thermopack': False}},
        {
            'medical_card': {
                'is_enabled': False,
                'issue_date': '2020-06-01T00:00:00+03:00',
            },
        },
        {
            'license_experience': {
                'total': '2010-01-01T00:00:00+03:00',
                'A': '2015-01-01T00:00:00+03:00',
                'B': '2017-10-01T00:00:00+03:00',
            },
        },
        {'courier_type': 'walking_courier'},
        {'orders_provider': {'taxi': True, 'lavka': False}},
        {'override_dict': {'g': 'h'}},
    ],
)
@pytest.mark.config(
    SELFEMPLOYED_EXTRA_REGISTRATION_FIELDS=[
        {'name': 'license_experience', 'enabled': True},
        {'name': 'medical_card', 'enabled': True},
        {'name': 'delivery', 'enabled': True},
        {'name': 'orders_provider', 'enabled': True},
        {'name': 'courier_type', 'enabled': True},
        {'name': 'default_str', 'enabled': True, 'default': 'str'},
        {'name': 'default_dict', 'enabled': True, 'default': {'a': 'b'}},
        {'name': 'disabled_dict', 'enabled': False, 'default': {'c': 'd'}},
        {'name': 'override_dict', 'enabled': True, 'default': {'e': 'f'}},
    ],
)
async def test_missing_license(
        se_web_context,
        patch,
        license_data,
        yet_another_driver_info,
        taxi_config,
        mock_partner_contracts,
):
    @patch('taxi.clients.parks.ParksClient.get_driver_info')
    async def get_driver_info(park_id: str, driver_id: str, **kwargs):
        assert park_id == 'old_park'
        assert driver_id == 'old_driver'
        return {
            'car_id': 'car',
            'first_name': 'И',
            'last_name': 'Ф',
            'license_expire_date': 'exp_date',
            'license_issue_date': 'iss_date',
            'middle_name': 'О',
            'park_city': 'Москва',
            **license_data,
            **yet_another_driver_info,
        }

    @patch('taxi.clients.parks.ParksClient.get_basic_car_info')
    async def get_basic_car_info(park_id, car_id, **kwargs):
        assert park_id == 'old_park'
        assert car_id == 'car'
        return {
            'brand': 'Kia',
            'color': 'Серый',
            'model': 'Rio',
            'number': 'К374НМ750',
            'year': 2016,
        }

    @mock_partner_contracts('/v1/register_partner/rus/')
    async def create_selfemployed_park(request: http.Request):
        request_json = request.json.copy()
        params = request_json.pop('params')
        assert request_json == {
            'flow': 'selfemployed',
            'rewrite': False,
            'new': True,
            'inquiry_id': 'selfemployed_id',
        }
        extra_args = yet_another_driver_info.copy()
        for field in taxi_config.get('SELFEMPLOYED_EXTRA_REGISTRATION_FIELDS'):
            if (
                    field['enabled']
                    and field['name'] not in yet_another_driver_info
            ):
                extra_args[field['name']] = field.get('default')

        assert params == {
            'company_address_street': '117000, ул. Хор, Москва',
            'car_brand': 'Kia',
            'car_color': 'Серый',
            'car_model': 'Rio',
            'car_number': 'К374НМ750',
            'car_year': 2016,
            'needs_rental_car': False,
            'first_name': 'Имя',
            'gas_stations_accepted': False,
            'hiring_source': None,
            'company_contact_fio': 'Фамилия Имя Отчество',
            'company_shortname': 'Фамилия Имя Отчество',
            'is_individual_entrepreneur': True,
            'uid': '',
            'company_inn': '7710123456',
            'last_name': 'Фамилия',
            'license_expire_date': 'exp_date',
            'license_issue_date': 'iss_date',
            'license_number': '000000',
            'license_series': '1111',
            'middle_name': 'Отчество',
            'park_city': 'Москва',
            'company_phone': '+7000',
            'company_address_index': '117000',
            'selfemployed_id': 'selfemployed_id',
            'default_str': 'str',
            'default_dict': {'a': 'b'},
            'override_dict': {'e': 'f'},
            **extra_args,
        }
        return {'inquiry_id': 'inquiry_id', 'status': 'status'}

    driver_data = {
        'id': 'selfemployed_id',
        'post_code': '117000',
        'address': 'ул. Хор, Москва',
        'from_park_id': 'old_park',
        'from_driver_id': 'old_driver',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'middle_name': 'Отчество',
        'phone': '+7000',
        'inn': '7710123456',
    }
    await actions.create_from_park_driver_pc(
        se_web_context, driver_data=driver_data,
    )


async def test_missing_old_park_car(
        se_web_context, patch, mock_partner_contracts,
):
    @patch('taxi.clients.parks.ParksClient.get_driver_info')
    async def get_driver_info(park_id: str, driver_id: str, **kwargs):
        assert park_id == 'old_park'
        assert driver_id == 'old_driver'
        return {
            'first_name': 'И',
            'last_name': 'Ф',
            'license_expire_date': 'exp_date',
            'license_issue_date': 'iss_date',
            'middle_name': 'О',
            'park_city': 'Москва',
            'license': {
                'number': '1111 000000',
                'normalized_number': '1111000000',
                'expiration_date': 'exp_date',
                'issue_date': 'iss_date',
            },
        }

    @mock_partner_contracts('/v1/register_partner/rus/')
    async def _register_park(request: http.Request):
        assert request.json == {
            'params': {
                'car_brand': 'Марка',
                'car_color': 'Желтый',
                'car_model': 'Модель',
                'car_number': 'Номер',
                'car_year': 2019,
                'needs_rental_car': True,
                'company_address_index': '117000',
                'company_address_street': '117000, ул. Хор, Москва',
                'company_inn': '7710123456',
                'company_phone': '+7000',
                'company_shortname': 'Фамилия Имя Отчество',
                'company_contact_fio': 'Фамилия Имя Отчество',
                'first_name': 'Имя',
                'gas_stations_accepted': True,
                'hiring_source': None,
                'is_individual_entrepreneur': True,
                'last_name': 'Фамилия',
                'license_expire_date': 'exp_date',
                'license_issue_date': 'iss_date',
                'license_number': '000000',
                'license_series': '1111',
                'middle_name': 'Отчество',
                'selfemployed_id': 'selfemployed_id',
                'park_city': 'Москва',
                'uid': '',
            },
            'inquiry_id': 'selfemployed_id',
            'flow': 'selfemployed',
            'new': True,
            'rewrite': False,
        }
        return {'inquiry_id': 'inquiry_id', 'status': 'status'}

    driver_data = {
        'id': 'selfemployed_id',
        'post_code': '117000',
        'address': 'ул. Хор, Москва',
        'from_park_id': 'old_park',
        'from_driver_id': 'old_driver',
        'first_name': 'Имя',
        'gas_stations_accepted': True,
        'last_name': 'Фамилия',
        'middle_name': 'Отчество',
        'phone': '+7000',
        'inn': '7710123456',
    }
    await actions.create_from_park_driver_pc(
        se_web_context, driver_data=driver_data,
    )


@pytest.mark.now('2020-01-01T12:00:00Z')
async def test_create_from_park_driver_sf(
        se_web_context: web_context.Context,
        mock_fleet_parks,
        mock_driver_profiles,
        mock_personal,
        mock_fleet_vehicles,
        mock_salesforce,
):
    @mock_fleet_parks('/v1/parks/list')
    async def _get_parks(request: http.Request):
        assert request.json == {'query': {'park': {'ids': ['parkid']}}}
        return {
            'parks': [
                {
                    'id': 'parkid',
                    'city_id': 'Москва',
                    'country_id': 'rus',
                    'demo_mode': True,
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'locale': 'ru',
                    'login': 'login',
                    'name': 'name',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _get_profile(request: http.Request):
        assert request.json == {'id_in_set': ['parkid_driverid']}
        print(request)
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_driverid',
                    'data': {
                        'license': {'pd_id': 'DL_PD_ID', 'country': 'RUS'},
                        'license_expire_date': '2025-09-01 00:00:00',
                        'license_issue_date': '2021-09-01 00:00:00',
                        'car_id': 'carid',
                        'platform_uid': 'passport_uid',
                    },
                },
            ],
        }

    @mock_personal('/v1/driver_licenses/retrieve')
    async def _retrieve_dl_pd(request: http.Request):
        assert request.json == {'id': 'DL_PD_ID', 'primary_replica': False}
        return {'value': '012345678901', 'id': 'DL_PD_ID'}

    @mock_fleet_vehicles('/v1/vehicles/retrieve')
    async def _get_car(request: http.Request):
        assert request.json == {'id_in_set': ['parkid_carid']}
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'parkid_carid',
                    'data': {
                        'brand': 'brand',
                        'model': 'model',
                        'number': 'number',
                        'number_normalized': 'number',
                        'color': 'color',
                        'year': '2020',
                    },
                },
            ],
        }

    @mock_salesforce('/services/data/v52.0/composite')
    async def _create(request: http.Request):
        assert request.json == {
            'compositeRequest': [
                {
                    'method': 'POST',
                    'referenceId': 'NewAccount',
                    'url': '/services/data/v46.0/sobjects/Account/',
                    'body': {
                        'RecordTypeId': 'RecordTypeAccount',
                        'Type': 'Selfemployed',
                        'SelfemloyedId__c': 'selfemployed_id',
                        'BillingPostalCode': 'post_code',
                        'BillingStreet': 'post_code, address',
                        'City__c': 'Москва',
                        'DateOfExpiration__c': '2025-09-01T00:00:00',
                        'DateOfIssuance__c': '2021-09-01T00:00:00',
                        'DriverLicenceCountry__c': 'rus',
                        'DriverLicenceNumber__c': '012345678901',
                        'FirstName': 'first_name',
                        'LastName': 'last_name',
                        'MiddleName': 'middle_name',
                        'Phone': '+phone',
                        'TIN__c': 'inn',
                        'Rent__c': False,
                        'GasStationContract__c': True,
                        'PassportId__c': 'passport_uid',
                    },
                },
                {
                    'method': 'POST',
                    'referenceId': 'NewOpportunity',
                    'url': '/services/data/v46.0/sobjects/Opportunity/',
                    'body': {
                        'RecordTypeId': 'RecordTypeOpportunity',
                        'Name': 'inn',
                        'AccountId': '@{NewAccount.id}',
                        'StageName': 'Scoring Completed',
                        'CloseDate': '2020-01-08',
                        'City__c': 'Москва',
                        'Platform__c': None,
                        'LeadId__c': None,
                    },
                },
                {
                    'method': 'POST',
                    'referenceId': 'NewAsset',
                    'url': '/services/data/v46.0/sobjects/Asset/',
                    'body': {
                        'RecordTypeId': 'RecordTypeAsset',
                        'Name': 'brand model',
                        'OpportunityId__c': '@{NewOpportunity.id}',
                        'PlateNo__c': 'number',
                        'Brand__c': 'brand',
                        'Model__c': 'model',
                        'Colour__c': 'color',
                        'ManufacturingYear__c': 2020,
                    },
                },
            ],
            'allOrNone': True,
        }
        return {
            'compositeResponse': [
                {
                    'body': {
                        'id': '003R00000025R22IAE',
                        'success': True,
                        'errors': [],
                    },
                    'httpHeaders': {
                        'Location': '/services/data/v52.0/sobjects/Account/003R00000025R22IAE',  # noqa: E501
                    },
                    'httpStatusCode': 201,
                    'referenceId': 'NewAccount',
                },
                {
                    'body': {
                        'id': 'a00R0000000iN4gIAE',
                        'success': True,
                        'errors': [],
                    },
                    'httpHeaders': {
                        'Location': '/services/data/v52.0/sobjects/Opportunity/a00R0000000iN4gIAE',  # noqa: E501
                    },
                    'httpStatusCode': 201,
                    'referenceId': 'NewOpportunity',
                },
                {
                    'body': {
                        'id': '100d0000000fjFAjoO',
                        'success': True,
                        'errors': [],
                    },
                    'httpHeaders': {
                        'Location': '/services/data/v52.0/sobjects/Asset/100d0000000fjFAjoO',  # noqa: E501
                    },
                    'httpStatusCode': 201,
                    'referenceId': 'NewAsset',
                },
            ],
        }

    account_id = await actions.create_from_park_driver_sf(
        se_web_context,
        {
            'from_park_id': 'parkid',
            'from_driver_id': 'driverid',
            'id': 'selfemployed_id',
            'post_code': 'post_code',
            'address': 'address',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'middle_name': 'middle_name',
            'phone': 'phone',
            'inn': 'inn',
            'gas_stations_accepted': True,
        },
    )
    assert account_id == '003R00000025R22IAE'


@pytest.mark.now('2020-01-01T12:00:00Z')
async def test_create_from_selfreg_sf(
        se_web_context: web_context.Context,
        mock_selfreg,
        mock_personal,
        mock_salesforce,
):
    @mock_selfreg('/internal/selfreg/v2/profile')
    async def _get_selfreg_profile(request: http.Request):
        assert request.query == {'selfreg_id': 'selfereg_id'}
        return {
            'locale': 'ru',
            'reported_to_zendesk': True,
            'token': 'token',
            'city': 'Москва',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'license_issue_date': '2015-09-01 00:00:00',
            'license_expire_date': '0001-01-01 00:00:00',
            'license_pd_id': 'DL_PD_ID',
            'middle_name': 'Отчество',
            'rent_option': 'rent',
            'selfreg_version': 'v2',
            'passport_uid': 'passport_uid',
        }

    @mock_personal('/v1/driver_licenses/retrieve')
    async def _store_pd(request: http.Request):
        assert request.json == {'id': 'DL_PD_ID', 'primary_replica': False}
        return {'value': '012345678901', 'id': 'DL_PD_ID'}

    @mock_salesforce('/services/data/v52.0/composite')
    async def _create(request: http.Request):
        assert request.json == {
            'compositeRequest': [
                {
                    'method': 'POST',
                    'referenceId': 'NewAccount',
                    'url': '/services/data/v46.0/sobjects/Account/',
                    'body': {
                        'RecordTypeId': 'RecordTypeAccount',
                        'Type': 'Selfemployed',
                        'SelfemloyedId__c': 'selfemployed_id',
                        'BillingPostalCode': 'post_code',
                        'BillingStreet': 'post_code, address',
                        'City__c': 'Москва',
                        'DateOfIssuance__c': '2015-09-01T00:00:00',
                        'DateOfExpiration__c': '2100-01-01T00:00:00',
                        'DriverLicenceCountry__c': 'rus',
                        'DriverLicenceNumber__c': '012345678901',
                        'FirstName': 'first_name',
                        'LastName': 'last_name',
                        'MiddleName': 'middle_name',
                        'Phone': '+phone',
                        'TIN__c': 'inn',
                        'Rent__c': True,
                        'GasStationContract__c': False,
                        'PassportId__c': 'passport_uid',
                    },
                },
                {
                    'method': 'POST',
                    'referenceId': 'NewOpportunity',
                    'url': '/services/data/v46.0/sobjects/Opportunity/',
                    'body': {
                        'RecordTypeId': 'RecordTypeOpportunity',
                        'Name': 'inn',
                        'AccountId': '@{NewAccount.id}',
                        'StageName': 'Scoring Completed',
                        'CloseDate': '2020-01-08',
                        'City__c': 'Москва',
                        'Platform__c': None,
                        'LeadId__c': None,
                    },
                },
            ],
            'allOrNone': True,
        }
        return {
            'compositeResponse': [
                {
                    'body': {
                        'id': '003R00000025R22IAE',
                        'success': True,
                        'errors': [],
                    },
                    'httpHeaders': {
                        'Location': '/services/data/v52.0/sobjects/Account/003R00000025R22IAE',  # noqa: E501
                    },
                    'httpStatusCode': 201,
                    'referenceId': 'NewAccount',
                },
                {
                    'body': {
                        'id': 'a00R0000000iN4gIAE',
                        'success': True,
                        'errors': [],
                    },
                    'httpHeaders': {
                        'Location': '/services/data/v52.0/sobjects/Opportunity/a00R0000000iN4gIAE',  # noqa: E501
                    },
                    'httpStatusCode': 201,
                    'referenceId': 'NewOpportunity',
                },
            ],
        }

    account_id = await actions.create_from_selfreg_sf(
        se_web_context,
        {
            'from_driver_id': 'selfereg_id',
            'id': 'selfemployed_id',
            'post_code': 'post_code',
            'address': 'address',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'middle_name': 'middle_name',
            'phone': 'phone',
            'inn': 'inn',
            'gas_stations_accepted': False,
        },
    )
    assert account_id == '003R00000025R22IAE'
