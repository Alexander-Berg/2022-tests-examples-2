import pytest

from hiring_taxiparks_gambling.internal import utils
from hiring_taxiparks_gambling.internal.salesforce import gambling


LOCALIZATIONS_FILE = 'localizations.json'

TRANSLATIONS = {
    'country_license.rus': {'ru': 'Россия', 'en': 'Russia'},
    'country_license.blr': {'ru': 'Беларусь', 'en': 'Belarus'},
    'country_license.kaz': {'ru': 'Казахстан', 'en': 'Kazakhstan'},
    'nationality.rus': {'en': 'Russia'},
    'nationality.blr': {'en': 'Belarus'},
    'nationality.kaz': {'en': 'Kazakhstan'},
    'registration.rus': {'ru': '', 'en': 'Registration in Russian Federation'},
}

ROUTE = '/v2/hiring-conditions/choose'


@pytest.mark.config(
    TAXIPARKS_GAMBLING_ENRICH_CONDITIONS_WITH_CARS=True,
    TAXIPARKS_GAMBLING_EXCLUDE_PARKS_WTIH_FIRED_STATUS=True,
)
async def test_simple_condition(
        taxi_hiring_taxiparks_gambling_web,
        driver_profiles_mock,
        load_json,
        mock_experiments3,
):
    # arrange
    expected_cars = load_json('expected_cars.json')
    request = load_json('requests.json')['simple_choose']
    exp3_responses = load_json('exp3_responses.json')
    experiments3_mock = mock_experiments3(exp3_responses['empty'])
    expected_exp3_request = load_json('expected_exp3_request.json')

    # act
    response = await taxi_hiring_taxiparks_gambling_web.post(
        ROUTE, json=request,
    )

    # assert
    result = [record for record in await response.json()]
    assert experiments3_mock.has_calls
    exp3_request = experiments3_mock.next_call()['request'].json
    assert exp3_request == expected_exp3_request
    assert len(result) == 1
    assert result[0]['sf_id'] == 'matched_condition'
    assert result[0]['cars'] == expected_cars
    assert not result[0].get('active')


@pytest.mark.config(
    TAXIPARKS_GAMBLING_ENRICH_CONDITIONS_WITH_CARS=True,
    TAXIPARKS_GAMBLING_EXCLUDE_PARKS_WTIH_FIRED_STATUS=True,
)
async def test_all_fired_conditions(
        taxi_hiring_taxiparks_gambling_web,
        driver_profiles_mock,
        load_json,
        mock_experiments3,
):
    # arrange
    request = load_json('requests.json')['fired_choose']
    exp3_responses = load_json('exp3_responses.json')
    experiments3_mock = mock_experiments3(exp3_responses['empty'])

    # act
    response = await taxi_hiring_taxiparks_gambling_web.post(
        ROUTE, json=request,
    )

    # assert
    result = [record for record in await response.json()]
    assert experiments3_mock.has_calls
    assert len(result) == 1
    assert result[0]['sf_id'] == 'fired_condition'
    assert result[0]['driver_status_in_park'] == 'deactivated'


@pytest.mark.config(
    TAXIPARKS_GAMBLING_ENRICH_CONDITIONS_WITH_CARS=False,
    TAXIPARKS_GAMBLING_EXCLUDE_PARKS_WTIH_FIRED_STATUS=True,
)
async def test_simple_condition_enrich_cars_not_enabled(
        taxi_hiring_taxiparks_gambling_web,
        driver_profiles_mock,
        load_json,
        mock_experiments3,
):
    # arrange
    request = load_json('requests.json')['simple_choose']
    exp3_responses = load_json('exp3_responses.json')
    experiments3_mock = mock_experiments3(exp3_responses['empty'])
    expected_exp3_request = load_json('expected_exp3_request.json')

    # act
    response = await taxi_hiring_taxiparks_gambling_web.post(
        ROUTE, json=request,
    )

    # assert
    result = [record for record in await response.json()]
    assert experiments3_mock.has_calls
    exp3_request = experiments3_mock.next_call()['request'].json
    assert exp3_request == expected_exp3_request
    assert len(result) == 1
    assert result[0]['sf_id'] == 'matched_condition'
    assert not result[0].get('cars')


@pytest.mark.parametrize(
    ('lead_name', 'experiment_name', 'target_length'),
    [
        ('mandatory_success', 'mandatory', 1),
        ('mandatory_fail', 'mandatory', 0),
        ('optional_success', 'optional', 2),
        ('optional_fail_one', 'optional', 1),
        ('optional_fail_all', 'optional', 3),
    ],
)
async def test_choose_with_experiment(
        choose_handler,
        filter_experiment,
        lead_name,
        experiment_name,
        target_length,
        driver_profiles_mock,
):
    filter_experiment(experiment_name)

    response = await choose_handler(lead_name)

    assert len(response) == target_length


async def test_tags_applied(
        choose_handler, filter_experiment, driver_profiles_mock,
):
    filter_experiment('simple')
    response = await choose_handler('with_experiment')

    assert 'success_experiment_applied' in response[0]['tags']
    assert 'fail_experiment_applied' in response[0]['tags']


@pytest.mark.parametrize(
    ('name', 'park'), [('rent', 'rent_park'), ('private', 'private_park')],
)
async def test_rent_logic(
        choose_handler, name, park, filter_experiment, driver_profiles_mock,
):
    filter_experiment('empty')
    response_ids = [rec['sf_id'] for rec in await choose_handler(name)]

    assert len(response_ids) == 2

    assert park in response_ids
    assert 'rent_and_private_park' in response_ids


@pytest.mark.parametrize(
    ('name', 'park'),
    [('first_park', 'second_park'), ('second_park', 'first_park')],
)
async def test_excluded_ids(
        choose_handler, name, park, filter_experiment, driver_profiles_mock,
):
    filter_experiment('empty')
    response_ids = [rec['sf_id'] for rec in await choose_handler(name)]

    assert len(response_ids) == 1
    assert park in response_ids


@pytest.mark.parametrize(
    ('comparison', 'results_set'),
    [
        ('is_eq', {'second'}),
        ('not_eq', {'first', 'third'}),
        ('is_lt', {'third'}),
        ('is_lte', {'second', 'third'}),
        ('is_gt', {'first'}),
        ('is_gte', {'first', 'second'}),
    ],
)
def test_eq_neq_gte_lte_comparisons(comparison, results_set, load_json):
    settings = load_json('comparisons.json')
    lead = settings['leads']['main']
    hiring_conditions = settings['hiring_conditions']['eq_neq_gte_lte']
    comparator_settings = settings['comparisons'][comparison]
    comparator = gambling.Comparator(**comparator_settings)
    result = {v['sf_id'] for v in comparator.apply(lead, hiring_conditions)}
    assert result == results_set


@pytest.mark.parametrize(
    ('comparison', 'results_set'),
    [('is_in', {'first'}), ('not_in', {'second'})],
)
def test_in_nin(comparison, results_set, load_json):
    settings = load_json('comparisons.json')
    lead = settings['leads']['main']
    hiring_conditions = settings['hiring_conditions']['in_nin']
    comparator_settings = settings['comparisons'][comparison]
    comparator = gambling.Comparator(**comparator_settings)
    result = {v['sf_id'] for v in comparator.apply(lead, hiring_conditions)}
    assert result == results_set


@pytest.mark.parametrize(
    ('comparison', 'results_set'),
    [('has_default', {'first'}), ('has_if_null_result', {'first'})],
)
def test_default_results(comparison, results_set, load_json):
    settings = load_json('comparisons.json')
    lead = settings['leads']['main']
    hiring_conditions = settings['hiring_conditions']['defaults']
    comparator_settings = settings['comparisons'][comparison]
    comparator = gambling.Comparator(**comparator_settings)
    result = {v['sf_id'] for v in comparator.apply(lead, hiring_conditions)}
    assert result == results_set


@pytest.mark.parametrize(
    ('lead_name', 'results_set'),
    [('is_true', {'is_true'}), ('is_false', {'is_true', 'is_false'})],
)
def test_fits(lead_name, results_set, load_json):
    settings = load_json('comparisons.json')
    lead = settings['leads'][lead_name]
    hiring_conditions = settings['hiring_conditions']['fits']
    comparator_settings = settings['comparisons']['fits']
    comparator = gambling.Comparator(**comparator_settings)
    result = {v['sf_id'] for v in comparator.apply(lead, hiring_conditions)}
    assert result == results_set


@pytest.mark.parametrize('name', ['fleet_type_non_existent'])
async def test_non_existent_fleet_type(
        choose_handler, name, filter_experiment, driver_profiles_mock,
):
    filter_experiment('empty')
    response_ids = [rec['sf_id'] for rec in await choose_handler(name)]

    assert not response_ids


@pytest.mark.parametrize(
    ('comparison', 'results_set'),
    [('includes', {'is_included'}), ('not_includes', {'is_not_included'})],
)
def test_includes_nincludes(comparison, results_set, load_json):
    settings = load_json('comparisons.json')
    lead = settings['leads']['array']
    hiring_conditions = settings['hiring_conditions']['includes_nincludes']
    comparator_settings = settings['comparisons'][comparison]
    comparator = gambling.Comparator(**comparator_settings)
    result = {v['sf_id'] for v in comparator.apply(lead, hiring_conditions)}
    assert result == results_set


@pytest.mark.parametrize(
    ('comparison', 'results_set'), [('common_value', {'first', 'third'})],
)
def test_common_value(comparison, results_set, load_json):
    settings = load_json('comparisons.json')
    lead = settings['leads']['main']
    hiring_conditions = settings['hiring_conditions']['search_common_value']
    comparator_settings = settings['comparisons'][comparison]
    comparator = gambling.Comparator(**comparator_settings)
    result = {v['sf_id'] for v in comparator.apply(lead, hiring_conditions)}
    assert result == results_set


async def test_dynamic_weight_experiment(
        filter_experiment, choose_handler, driver_profiles_mock,
):
    filter_experiment('dynamic_weight')
    response_ids = [
        rec['sf_id'] for rec in await choose_handler('dynamic_weight')
    ]
    assert response_ids == ['tag_experiment_park1']
    assert len(response_ids) == 1


@pytest.mark.config(TAXIPARKS_GAMBLING_EXCLUDE_PARKS_WTIH_FIRED_STATUS=True)
async def test_filtering_parks_by_license_id(
        filter_experiment, choose_handler, driver_profiles_mock,
):
    # arrange
    filter_experiment('empty')
    # act
    response_ids = [
        rec['sf_id'] for rec in await choose_handler('filtering_by_license_id')
    ]
    # assert
    assert response_ids == ['matched_condition']
    assert len(response_ids) == 1


async def test_filtering_parks_by_license_id_failed(
        filter_experiment, choose_handler, driver_profiles_fail_mock,
):
    # arrange
    filter_experiment('empty')
    # act
    response_ids = [
        rec['sf_id'] for rec in await choose_handler('filtering_by_license_id')
    ]
    # assert
    assert sorted(response_ids) == ['matched_condition', 'matched_condition 2']
    assert len(response_ids) == 2


@pytest.mark.translations(hiring_suggests=TRANSLATIONS)
@pytest.mark.parametrize(
    'request_name',
    [
        'localization_not_full_ru',
        'localization_en',
        'localization_empty_field',
        'localization_fake_locale',
    ],
)
async def test_localization(
        choose_handler,
        filter_experiment,
        load_json,
        request_name,
        driver_profiles_mock,
):
    filter_experiment('empty')
    response = await choose_handler(request_name)
    extra = response[0].get('extra')
    expected_extra = load_json(LOCALIZATIONS_FILE)[request_name]
    assert extra == expected_extra


async def test_casefold():
    assert utils.casefold_value('QWERTYUIO') == 'qwertyuio'
    assert utils.casefold_value([{'key': 'ßQD'}, 'O']) == [
        {'key': 'ssqd'},
        'o',
    ]
    assert utils.casefold_value('7Г') == '7г'
    assert utils.casefold_value('') == ''
