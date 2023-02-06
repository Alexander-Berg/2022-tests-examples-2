import pytest


@pytest.fixture
def qc_service_response(mockserver, load):
    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_service_response(request):
        print('bla-bla-bla request: ', request)
        if (
                request.args['type'] == 'driver'
                and request.args['id'] == '1234_testdriver'
        ):
            return mockserver.make_response(load('qcs-response.json'))

        if (
                request.args['type'] == 'car'
                and request.args['id'] == '1234_12345'
        ):
            return mockserver.make_response(load('qcs-car-response.json'))

        return mockserver.make_response('', 404)


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_DRIVERCLIENTCHAT_SPEECH_PARAMS={
        'ru': {
            'recognizer': 'yandex_speechkit',
            'vocalizer': 'undefined',
            'language_code': 'ru_RU',
        },
    },
)
def test_basic(
        taxi_driver_protocol,
        load_json,
        qc_service_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

    params = {'db': '1234', 'session': 'qwerty', 'exam': 'dkvu'}

    response = taxi_driver_protocol.get(
        'driver/qc/state', params=params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('full-answer.json')


@pytest.mark.now('2018-01-22T00:00:00Z')
def test_another_exam(
        taxi_driver_protocol,
        load_json,
        qc_service_response,
        driver_authorizer_service,
):
    """
    We  request dkk info, but /qcs/api/v1/state returns info only about dkvu.
    So will be response, contains only request code
    """
    driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

    exam = 'dkk'

    params = {'db': '1234', 'session': 'qwerty', 'exam': exam}

    response = taxi_driver_protocol.get(
        'driver/qc/state', params=params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == {'code': exam}


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_QC_SETTINGS={'sync_mode': 'on', 'sync_dkk': 'on'},
)
def test_car_dkk_sync_on(
        taxi_driver_protocol,
        load_json,
        qc_service_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

    exam = 'dkk'

    params = {'db': '1234', 'session': 'qwerty', 'exam': exam}

    response = taxi_driver_protocol.get(
        'driver/qc/state', params=params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('full-car-dkk-answer.json')


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_QC_SETTINGS={'sync_mode': 'on', 'sync_dkk': 'dry-run'},
)
def test_car_dkk_dry_run_without_experiment(
        taxi_driver_protocol,
        load_json,
        qc_service_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

    exam = 'dkk'

    params = {'db': '1234', 'session': 'qwerty', 'exam': exam}

    response = taxi_driver_protocol.get(
        'driver/qc/state', params=params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == {'code': exam}


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_QC_SETTINGS={'sync_mode': 'on', 'sync_dkk': 'dry-run'},
)
@pytest.mark.driver_experiments('use_car_dkk')
def test_car_dkk_dry_run_with_experiment(
        taxi_driver_protocol,
        db,
        load_json,
        qc_service_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

    exam = 'dkk'

    params = {'db': '1234', 'session': 'qwerty', 'exam': exam}

    response = taxi_driver_protocol.get(
        'driver/qc/state', params=params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('full-car-dkk-answer.json')


@pytest.mark.now('2018-01-22T00:00:00Z')
def test_branding(
        taxi_driver_protocol,
        load_json,
        qc_service_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

    exam = 'branding'

    params = {'db': '1234', 'session': 'qwerty', 'exam': exam}

    response = taxi_driver_protocol.get(
        'driver/qc/state', params=params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('full-branding-answer.json')


@pytest.mark.now('2018-01-22T00:00:00Z')
def test_sts(
        taxi_driver_protocol,
        load_json,
        qc_service_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

    exam = 'sts'

    params = {'db': '1234', 'session': 'qwerty', 'exam': exam}

    response = taxi_driver_protocol.get(
        'driver/qc/state', params=params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('full-sts-answer.json')


@pytest.fixture
def qc_service_tutorial_response(mockserver, load):
    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_service_response(request):
        data = load('qcs-response-newbie.json')
        return mockserver.make_response(data)


@pytest.fixture
def qc_service_tutorial_not_newbie_response(mockserver, load):
    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_service_response(request):
        data = load('qcs-response-tutorial-not-newbie.json')
        return mockserver.make_response(data)


@pytest.mark.now('2018-01-22T00:00:00Z')
class TestNewbie:
    @pytest.mark.redis_store(['set', 'DKK:1234:testdriver:LIST', 'test_items'])
    @pytest.mark.redis_store(
        ['set', 'DKK:1234:testdriver:ITEMS', 'test_items'],
    )
    @pytest.mark.config(QC_IS_NEWBIE_SOURCE={'__default__': 'redis'})
    @pytest.mark.usefixtures('qc_service_tutorial_response')
    def test_dkvu_newbie_by_redis(
            self,
            taxi_driver_protocol,
            load_json,
            qc_service_tutorial_response,
            driver_authorizer_service,
    ):
        """
        Checks driver is newbie:
        1. 'tutorial_code' will be returned
        2. 'confirmation_text' will be nondefault.

        We have info in Dkk collections, so driver isn't newbie for Dkk,
        but we don't have info in Dkvu collections, so driver is newbie
        for Dkvu
        As we pass 'dkvu' exam, so we should get newbie info
        """
        driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

        params = {'db': '1234', 'session': 'qwerty', 'exam': 'dkvu'}

        response = taxi_driver_protocol.get(
            'driver/qc/state',
            params=params,
            headers={'Accept-Language': 'ru'},
        )
        assert response.status_code == 200
        assert response.json() == load_json('full-answer-newbie.json')

    @pytest.mark.config(
        QC_IS_NEWBIE_SOURCE={'__default__': 'redis', 'dkvu': 'qc'},
    )
    @pytest.mark.redis_store(
        ['set', 'DKB:Dkvu:1234:testdriver:LIST', 'test_items'],
    )
    @pytest.mark.usefixtures('qc_service_tutorial_response')
    def test_dkvu_newbie_by_qc(
            self,
            taxi_driver_protocol,
            load_json,
            qc_service_tutorial_response,
            driver_authorizer_service,
    ):
        driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

        params = {'db': '1234', 'session': 'qwerty', 'exam': 'dkvu'}

        response = taxi_driver_protocol.get(
            'driver/qc/state',
            params=params,
            headers={'Accept-Language': 'ru'},
        )
        assert response.status_code == 200
        assert response.json() == load_json('full-answer-newbie.json')

    @pytest.mark.config(QC_IS_NEWBIE_SOURCE={'__default__': 'redis'})
    @pytest.mark.redis_store(
        ['set', 'DKB:Dkvu:1234:testdriver:LIST', 'test_items'],
    )
    @pytest.mark.usefixtures('qc_service_tutorial_response')
    def test_dkvu_not_newbie_by_redis(
            self,
            taxi_driver_protocol,
            load_json,
            qc_service_tutorial_response,
            driver_authorizer_service,
    ):
        """
        Checks driver isn't newbie:
        1. no 'tutorial_code' will be returned
        2. 'confirmation_text' will be default.

        We haven't info in Dkk collections, so driver is newbie for Dkk,
        but we have info in Dkvu collections, so driver is newbie for Dkvu
        As we pass 'dkvu' exam, so we should get nonnewbie info
        """
        driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

        params = {'db': '1234', 'session': 'qwerty', 'exam': 'dkvu'}

        response = taxi_driver_protocol.get(
            'driver/qc/state',
            params=params,
            headers={'Accept-Language': 'ru'},
        )
        assert response.status_code == 200
        assert response.json() == load_json('full-answer-not-newbie.json')

    @pytest.mark.config(
        QC_IS_NEWBIE_SOURCE={'__default__': 'redis', 'dkvu': 'qc'},
    )
    @pytest.mark.usefixtures('qc_service_tutorial_not_newbie_response')
    def test_dkvu_not_newbie_by_qc(
            self,
            taxi_driver_protocol,
            load_json,
            qc_service_tutorial_not_newbie_response,
            driver_authorizer_service,
    ):
        driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

        params = {'db': '1234', 'session': 'qwerty', 'exam': 'dkvu'}

        response = taxi_driver_protocol.get(
            'driver/qc/state',
            params=params,
            headers={'Accept-Language': 'ru'},
        )
        assert response.status_code == 200
        assert response.json() == load_json('full-answer-not-newbie.json')


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_DRIVERCLIENTCHAT_SPEECH_PARAMS={
        'ru': {
            'recognizer': 'yandex_speechkit',
            'vocalizer': 'undefined',
            'language_code': 'ru_RU',
        },
    },
)
@pytest.mark.filldb(localization_taximeter_backend_driver_messages='no_title')
def test_translation(
        taxi_driver_protocol,
        load_json,
        qc_service_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1234', 'qwerty', 'testdriver')

    response = taxi_driver_protocol.get(
        'driver/qc/state?db=1234&session=qwerty&exam=dkvu',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 404


@pytest.fixture
def qc_service_response500(mockserver):
    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_service_response(request):
        return mockserver.make_response('', 500)


@pytest.mark.now('2018-01-22T00:00:00Z')
def test_qcs_error(
        taxi_driver_protocol,
        load_json,
        qc_service_response500,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1234', 'qwerty', 'test_driver')

    params = {'db': '1234', 'session': 'qwerty', 'exam': 'dkvu'}

    response = taxi_driver_protocol.get(
        'driver/qc/state', params=params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 500


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_DRIVERCLIENTCHAT_SPEECH_PARAMS={
        'ru': {
            'recognizer': 'yandex_speechkit',
            'vocalizer': 'undefined',
            'language_code': 'ru_RU',
        },
    },
)
def test_no_exam(
        taxi_driver_protocol,
        load_json,
        qc_service_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1234', 'qwerty', 'test_driver')

    params = {'db': '1234', 'session': 'qwerty'}
    response = taxi_driver_protocol.get(
        'driver/qc/state', params=params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 400
