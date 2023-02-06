import pytest

from tests_bank_applications import common
from tests_bank_applications import utils

AVATARS_HOST = 'avatars.mdst.yandex.net'

REQUIRED_HEADERS = {
    'X-Yandex-UID': '100000',
    'X-Yandex-BUID': '44444444-4444-4444-4444-444444444444',
    'X-YaBank-SessionUUID': '55555555-5555-5555-5555-555555555555',
    'X-YaBank-PhoneID': 'phone_id',
    'X-Ya-User-Ticket': 'user_ticket',
}

VALID_ENTITIES = [
    ('name', 'абвгд'),
    ('surname', 'abcde'),
    ('middle_name', 'abcde'),
    ('birth_date', '01.01.1970'),
    # ('citizenship', 'rus'),
    # ('gender', 'жен'),
    # ('gender', 'муж'),
    ('birth_place', 'Москва'),
    ('number', '0102030405'),
    ('issue_date', '01.01.2070'),
    ('issued_by', 'МВД РФ'),
    ('subdivision', '110-630'),
]

INVALID_ENTITIES = [
    ('birth_date', '1.01.1970'),
    ('birth_date', '01,01.1970'),
    ('birth_date', 'dd.mm.yyyy'),
    # ('gender', 'ж'),
    # ('gender', 'абв'),
    ('number', '010203405'),
    ('number', 'ab0020405'),
    ('issue_date', '1.01.1970'),
    ('issue_date', '01,01.1970'),
    ('birth_date', 'dd.mm.yyyy'),
    ('subdivision', '110_630'),
]


@pytest.mark.parametrize('response_type', ['400', '500'])
@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_cv_bad_response(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_forms_mock,
        bank_agreements_mock,
        pgsql,
        response_type,
):
    application_id = '22222222-1111-1111-1111-111111111111'
    image_blob = b'image jpeg'
    page_number = 'FIRST'
    image_name = 'auto_generated_image_name'
    group_id = 100

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number,
        avatars_mds_mock,
        group_id,
        image_name,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_bad_response(response_type)

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    pg_application_after = utils.select_application(pgsql, application_id)

    common.check_equal_without_add_params(
        pg_application_after, pg_application_before,
    )

    assert (
        pg_application_before.additional_params
        != pg_application_after.additional_params
    )
    add_params = pg_application_after.additional_params

    page = common.PASSPORT_PAGE_FORMAT.format(page_number)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id, image_name,
    )

    assert avatars_mds_mock.put_unnamed_handler.has_calls

    assert response.status_code == 200
    assert response.json() == {'status': 'SAVED'}


@pytest.mark.config(
    BANK_AVATARS_IMAGES_HOST=AVATARS_HOST, BANK_CV_RECOGNITION_ACCURACY=0.5,
)
async def test_kyc_upload_passport_cv_good_accuracy_on_second_page(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        bank_agreements_mock,
        ocr_recognize_mock,
        bank_forms_mock,
        pgsql,
):
    application_id = '22222222-1111-1111-1111-111111111111'
    image_blob = b'image jpeg'
    page_number = 'SECOND'
    image_name = 'auto_generated_image_name'
    group_id = 100

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number,
        avatars_mds_mock,
        group_id,
        image_name,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')
    bank_forms_mock.set_http_status_code(200)
    ocr_recognize_mock.set_entities(
        [ocr_recognize_mock.make_entity('birth_date', '01.01.2000', 0.9)],
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    pg_application_after = utils.select_application(pgsql, application_id)

    common.check_equal_without_add_params(
        pg_application_after, pg_application_before,
    )

    assert (
        pg_application_before.additional_params
        != pg_application_after.additional_params
    )
    add_params = pg_application_after.additional_params

    page = common.PASSPORT_PAGE_FORMAT.format(page_number)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id, image_name,
    )

    assert avatars_mds_mock.put_unnamed_handler.has_calls

    assert response.status_code == 200
    assert response.json() == {'status': 'SAVED'}


# по соответствует формату и accuracy > BANK_CV_RECOGNIZE_ACCURACY
@pytest.mark.skip(reason='unused handler')
@pytest.mark.parametrize('text_type,text', VALID_ENTITIES)
@pytest.mark.config(
    BANK_AVATARS_IMAGES_HOST=AVATARS_HOST, BANK_CV_RECOGNITION_ACCURACY=0.5,
)
async def test_kyc_upload_passport_cv_success_recognition(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_agreements_mock,
        bank_forms_mock,
        pgsql,
        text_type,
        text,
):
    application_id = '22222222-1111-1111-1111-111111111111'
    image_blob = b'image jpeg'
    page_number = 'FIRST'
    image_name = 'auto_generated_image_name'
    group_id = 100

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number,
        avatars_mds_mock,
        group_id,
        image_name,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')
    bank_forms_mock.set_http_status_code(200)
    ocr_recognize_mock.set_entities(
        [ocr_recognize_mock.make_entity(text, text_type, 0.61)],
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    pg_application_after = utils.select_application(pgsql, application_id)

    common.check_equal_without_add_params(
        pg_application_after, pg_application_before,
    )

    assert (
        pg_application_before.additional_params
        != pg_application_after.additional_params
    )
    add_params = pg_application_after.additional_params

    page = common.PASSPORT_PAGE_FORMAT.format(page_number)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id, image_name,
    )

    assert avatars_mds_mock.put_unnamed_handler.has_calls

    assert response.status_code == 200
    assert response.json() == {'status': 'RECOGNIZED'}


@pytest.mark.parametrize('text_type,text', VALID_ENTITIES)
@pytest.mark.config(
    BANK_AVATARS_IMAGES_HOST=AVATARS_HOST, BANK_CV_RECOGNITION_ACCURACY=0.5,
)
async def test_kyc_upload_passport_cv_success_but_bad_bank_forms_saving(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_agreements_mock,
        bank_forms_mock,
        pgsql,
        text_type,
        text,
):
    application_id = '22222222-1111-1111-1111-111111111111'
    image_blob = b'image jpeg'
    page_number = 'FIRST'
    image_name = 'auto_generated_image_name'
    group_id = 100

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number,
        avatars_mds_mock,
        group_id,
        image_name,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')
    bank_forms_mock.set_http_status_code(400)

    ocr_recognize_mock.set_entities(
        [ocr_recognize_mock.make_entity(text, text_type, 0.61)],
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    pg_application_after = utils.select_application(pgsql, application_id)

    common.check_equal_without_add_params(
        pg_application_after, pg_application_before,
    )

    assert (
        pg_application_before.additional_params
        != pg_application_after.additional_params
    )
    add_params = pg_application_after.additional_params

    page = common.PASSPORT_PAGE_FORMAT.format(page_number)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id, image_name,
    )

    assert avatars_mds_mock.put_unnamed_handler.has_calls

    assert response.status_code == 200
    assert response.json() == {'status': 'SAVED'}


# не соответствует формату, но accuracy > BANK_CV_RECOGNIZE_ACCURACY
@pytest.mark.parametrize(
    'text_type,text,bank_forms_status',
    list(map(lambda x: x + (200,), INVALID_ENTITIES))
    + list(map(lambda x: x + (400,), INVALID_ENTITIES)),
)
@pytest.mark.config(
    BANK_AVATARS_IMAGES_HOST=AVATARS_HOST, BANK_CV_RECOGNITION_ACCURACY=0.5,
)
async def test_kyc_upload_passport_cv_bad_data_given(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_forms_mock,
        bank_agreements_mock,
        pgsql,
        text_type,
        text,
        bank_forms_status,
):
    application_id = '22222222-1111-1111-1111-111111111111'
    image_blob = b'image jpeg'
    page_number = 'FIRST'
    image_name = 'auto_generated_image_name'
    group_id = 100

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number,
        avatars_mds_mock,
        group_id,
        image_name,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')
    bank_forms_mock.set_http_status_code(bank_forms_status)
    ocr_recognize_mock.set_entities(
        [ocr_recognize_mock.make_entity(text, text_type, 0.61)],
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    pg_application_after = utils.select_application(pgsql, application_id)

    common.check_equal_without_add_params(
        pg_application_after, pg_application_before,
    )

    assert (
        pg_application_before.additional_params
        != pg_application_after.additional_params
    )
    add_params = pg_application_after.additional_params

    page = common.PASSPORT_PAGE_FORMAT.format(page_number)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id, image_name,
    )

    assert avatars_mds_mock.put_unnamed_handler.has_calls

    assert response.status_code == 200
    assert response.json() == {'status': 'SAVED'}


#  accuracy < BANK_CV_RECOGNIZE_ACCURACY
@pytest.mark.parametrize('text_type,text', VALID_ENTITIES + INVALID_ENTITIES)
@pytest.mark.config(
    BANK_AVATARS_IMAGES_HOST=AVATARS_HOST, BANK_CV_RECOGNITION_ACCURACY=0.9,
)
async def test_kyc_upload_passport_cv_bad_data_or_accuracy(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_forms_mock,
        bank_agreements_mock,
        pgsql,
        text_type,
        text,
):
    application_id = '22222222-1111-1111-1111-111111111111'
    image_blob = b'image jpeg'
    page_number = 'FIRST'
    image_name = 'auto_generated_image_name'
    group_id = 100

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number,
        avatars_mds_mock,
        group_id,
        image_name,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')
    bank_forms_mock.set_http_status_code(200)
    ocr_recognize_mock.set_entities(
        [ocr_recognize_mock.make_entity(text, text_type, 0.61)],
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    pg_application_after = utils.select_application(pgsql, application_id)

    common.check_equal_without_add_params(
        pg_application_after, pg_application_before,
    )

    assert (
        pg_application_before.additional_params
        != pg_application_after.additional_params
    )
    add_params = pg_application_after.additional_params

    page = common.PASSPORT_PAGE_FORMAT.format(page_number)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id, image_name,
    )

    assert avatars_mds_mock.put_unnamed_handler.has_calls

    assert response.status_code == 200
    assert response.json() == {'status': 'SAVED'}


@pytest.mark.config(
    BANK_AVATARS_IMAGES_HOST=AVATARS_HOST, BANK_CV_RECOGNITION_ACCURACY=0.5,
)
async def test_kyc_upload_passport_cv_invalid_status(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_forms_mock,
        bank_agreements_mock,
        pgsql,
):
    application_id = '22222222-1111-1111-1111-111111111111'
    image_blob = b'image jpeg'
    page_number = 'FIRST'
    image_name = 'auto_generated_image_name'
    group_id = 100

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number,
        avatars_mds_mock,
        group_id,
        image_name,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('invalid')
    bank_forms_mock.set_http_status_code(200)
    ocr_recognize_mock.set_entities(
        [ocr_recognize_mock.make_entity('abc', 'name', 0.61)],
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    pg_application_after = utils.select_application(pgsql, application_id)

    common.check_equal_without_add_params(
        pg_application_after, pg_application_before,
    )

    assert (
        pg_application_before.additional_params
        != pg_application_after.additional_params
    )
    add_params = pg_application_after.additional_params

    page = common.PASSPORT_PAGE_FORMAT.format(page_number)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id, image_name,
    )

    assert avatars_mds_mock.put_unnamed_handler.has_calls

    assert response.status_code == 200
    assert response.json() == {'status': 'SAVED'}


@pytest.mark.config(
    BANK_AVATARS_IMAGES_HOST=AVATARS_HOST, BANK_CV_RECOGNITION_ACCURACY=0.5,
)
async def test_kyc_upload_passport_cv_not_existing_entity(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_forms_mock,
        bank_agreements_mock,
        pgsql,
):
    application_id = '22222222-1111-1111-1111-111111111111'
    image_blob = b'image jpeg'
    page_number = 'FIRST'
    image_name = 'auto_generated_image_name'
    group_id = 100

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number,
        avatars_mds_mock,
        group_id,
        image_name,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')
    bank_forms_mock.set_http_status_code(200)
    ocr_recognize_mock.set_entities(
        [ocr_recognize_mock.make_entity('abc', 'exname', 0.61)],
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    pg_application_after = utils.select_application(pgsql, application_id)

    common.check_equal_without_add_params(
        pg_application_after, pg_application_before,
    )

    assert (
        pg_application_before.additional_params
        != pg_application_after.additional_params
    )
    add_params = pg_application_after.additional_params

    page = common.PASSPORT_PAGE_FORMAT.format(page_number)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id, image_name,
    )

    assert avatars_mds_mock.put_unnamed_handler.has_calls

    assert response.status_code == 200
    assert response.json() == {'status': 'SAVED'}
