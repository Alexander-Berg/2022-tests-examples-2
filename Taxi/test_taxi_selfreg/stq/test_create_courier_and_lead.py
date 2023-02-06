import pytest

from generated.models import hiring_selfreg_forms as hiring_sf_models
from taxi.stq import async_worker_ng

from taxi_selfreg import db
from taxi_selfreg.stq import create_courier_and_lead

VACANCY_RESPONSE_BICYCLE = hiring_sf_models.ResponseInternalEdaVacancyChoose(
    service='eda',
    success=True,
    vacancy='eda_bicycle',
    vehicle_type='bicycle',
    form_data={'ProjectType__c': 'eda'},
)

VACANCY_RESPONSE_CAR = hiring_sf_models.ResponseInternalEdaVacancyChoose(
    service='eda',
    success=True,
    vacancy='eda_car',
    vehicle_type='car',
    form_data={
        'vacancy': 'курьер_яндекс_еда_вакансия',
        'Vacancy__c': 'Courier',
        'type_of_employment_form': 'toef_delivery',
        'requires_hiring_supply_response': False,
        'hiring_supply_checked': True,
        'hiring_supply_is_desired_vacancy': True,
        'workflow': 'new_courier',
        'courier_transport_type': 'courier_with_auto',
        'CourierType__c': 'vehicle',
        'ProjectType__c': 'eda',
    },
)


HIRING_API_RESPONSE = {
    'body': {
        'code': 'SUCCESS',
        'details': {'accepted_fields': ['name', 'phone']},
        'message': 'Accepted',
    },
    'status': 200,
}


@pytest.mark.parametrize(
    'exec_tries,sf_external_id,courier_id',
    [
        pytest.param(0, '000000005a7581722016667706734a33', 1234567),
        pytest.param(700, None, None),
    ],
)
@pytest.mark.client_experiments3(
    file_with_default_response='exp3_all_methods_enabled.json',
)
async def test_create_courier_and_lead(
        stq3_context,
        taxi_selfreg,
        mock_internal_v1_eda_data,
        mock_hiring_api_v2_leads_upsert,
        exec_tries,
        sf_external_id,
        courier_id,
        mockserver,
):
    mock_hiring_api_v2_leads_upsert([HIRING_API_RESPONSE])

    @mockserver.json_handler(
        '/eda_core/api/v1/general-information/couriers/create-or-update',
    )
    def _mock_eda_core_courier_create(reqeust):
        assert reqeust.json['birthday'] == '2000-01-01'
        assert reqeust.json['project_type'] == 'eda'
        return mockserver.make_response(status=200, json={'id': 1234567})

    task_info = async_worker_ng.TaskInfo(
        id='task_id',
        exec_tries=exec_tries,
        reschedule_counter=0,
        queue='taxi_selfreg_create_courier_and_lead',
    )

    await create_courier_and_lead.task(
        context=stq3_context,
        task_info=task_info,
        token_instance='token1',
        city_id='Москва',
        vacancy_vacancy=VACANCY_RESPONSE_BICYCLE.vacancy,
        vacancy_service=VACANCY_RESPONSE_BICYCLE.service,
        vacancy_form_data=VACANCY_RESPONSE_BICYCLE.form_data,
        vacancy_vehicle_type=VACANCY_RESPONSE_BICYCLE.vehicle_type,
    )

    profile = await db.get_profile_by_token(
        token='token1', selfreg_profiles=stq3_context.mongo.selfreg_profiles,
    )
    if profile:
        assert profile.sf_external_id == sf_external_id
        assert profile.courier_id == courier_id
    else:
        assert False


@pytest.mark.config(
    TAXIMETER_SELFREG_REGISTRATION_PARAMETER_SETTINGS={
        'bypass_enabled': True,
        'bypass_mapping': [
            {'bypass_name': 'utm_source__c', 'original_name': 'utm_source'},
            {'bypass_name': '', 'original_name': 'some_excluded_parameter'},
        ],
    },
)
@pytest.mark.client_experiments3(
    file_with_default_response='exp3_all_methods_enabled.json',
)
async def test_create_courier_and_lead_passed_parameters(
        stq3_context,
        taxi_selfreg,
        mock_eda_core_courier_create,
        mock_internal_v1_eda_data,
        mock_hiring_api_v2_leads_upsert,
        load_json,
):
    mock_hiring_api_v2_leads_upsert([HIRING_API_RESPONSE])

    task_info = async_worker_ng.TaskInfo(
        id='task_id',
        exec_tries=0,
        reschedule_counter=0,
        queue='taxi_selfreg_create_courier_and_lead',
    )

    await create_courier_and_lead.task(
        context=stq3_context,
        task_info=task_info,
        token_instance='token2',
        city_id='Москва',
        vacancy_vacancy=VACANCY_RESPONSE_CAR.vacancy,
        vacancy_service=VACANCY_RESPONSE_CAR.service,
        vacancy_form_data=VACANCY_RESPONSE_CAR.form_data,
        vacancy_vehicle_type=VACANCY_RESPONSE_CAR.vehicle_type,
    )

    profile = await db.get_profile_by_token(
        token='token2', selfreg_profiles=stq3_context.mongo.selfreg_profiles,
    )
    if profile:
        assert profile.sf_external_id == '000000005a7581722016667706734a34'
        assert profile.courier_id == 1234567
    else:
        assert False
