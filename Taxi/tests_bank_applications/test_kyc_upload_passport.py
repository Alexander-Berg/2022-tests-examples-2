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


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_not_authorized(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        bank_agreements_mock,
        ocr_recognize_mock,
):
    application_id = '11111111-1111-1111-1111-111111111111'
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

    ocr_recognize_mock.set_status('success')

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    assert response.status_code == 401
    assert response.json()['message'] == 'Unauthorized'


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_bank_applications_db_invalid_application_id(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        bank_agreements_mock,
        ocr_recognize_mock,
):
    application_id = '11111111-1111-1111-1111-111111111110'
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

    ocr_recognize_mock.set_status('success')

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    assert response.status_code == 400
    assert response.json()['message'] == 'invalid application_id'


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_bank_applications_db_invalid_page_number_1(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        bank_agreements_mock,
        ocr_recognize_mock,
):
    application_id = '11111111-1111-1111-1111-111111111111'
    image_blob = b'image jpeg'
    page_number = '239847'

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

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    assert response.status_code == 400
    assert response.json()['message'] == 'Failed to parse request'


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_bank_applications_db_invalid_page_number_2(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        bank_agreements_mock,
        ocr_recognize_mock,
):
    application_id = '11111111-1111-1111-1111-111111111111'
    image_blob = b'image jpeg'
    page_number = 'THIRD'

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

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    assert response.status_code == 400
    assert response.json()['message'] == 'Failed to parse request'


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_avatars_mds_check_invalid_data_format(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        bank_agreements_mock,
):
    application_id = '11111111-1111-1111-1111-111111111111'
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

    avatars_mds_mock.invalid_data_format = True

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    assert response.status_code == 415
    assert avatars_mds_mock.put_unnamed_handler.has_calls


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_avatars_mds_bad_request(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        bank_agreements_mock,
):
    application_id = '11111111-1111-1111-1111-111111111111'
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

    avatars_mds_mock.bad_request = True

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    assert response.status_code == 400
    assert avatars_mds_mock.put_unnamed_handler.has_calls


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_invalid_application_status(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        bank_agreements_mock,
):
    application_id = '11111111-1111-1111-1111-333333333333'
    image_blob = b'image jpeg 1'
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

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    assert response.status_code == 400
    assert (
        response.json()['message']
        == 'application status not exist or is invalid'
    )


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_no_application_status(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        bank_agreements_mock,
):
    application_id = '11111111-1111-1111-1111-444444444444'
    image_blob = b'image jpeg 1'
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

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    assert response.status_code == 400
    assert (
        response.json()['message']
        == 'application status not exist or is invalid'
    )


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_no_such_application_status(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        bank_agreements_mock,
):
    application_id = '11111111-1111-1111-1111-555555555555'
    image_blob = b'image jpeg 1'
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

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    assert response.status_code == 500


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_bank_applications_db_1(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_agreements_mock,
        pgsql,
):
    application_id = '11111111-1111-1111-1111-111111111111'
    image_blob = b'image jpeg 1'
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

    ocr_recognize_mock.set_status('success')

    pg_application_before = utils.select_application(pgsql, application_id)

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
    add_params.pop(page)
    assert pg_application_before.additional_params == add_params

    assert response.status_code == 200
    assert avatars_mds_mock.put_unnamed_handler.has_calls


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_bank_applications_db_1_1(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_agreements_mock,
        pgsql,
):
    # first request
    application_id = '11111111-1111-1111-1111-111111111111'
    image_blob = b'image jpeg'
    page_number = 'FIRST'

    image_name1 = 'auto_generated_image_name'
    group_id1 = 100

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number,
        avatars_mds_mock,
        group_id1,
        image_name1,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')

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
        AVATARS_HOST, group_id1, image_name1,
    )

    assert response.status_code == 200
    assert avatars_mds_mock.put_unnamed_handler.has_calls

    # second request

    image_blob = b'image jpeg ***'

    image_name2 = 'other_image_name'
    group_id2 = 101

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number,
        avatars_mds_mock,
        group_id2,
        image_name2,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')

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
    assert len(add_params[page]) == 2
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id1, image_name1,
    )
    assert add_params[page][1] == common.get_image_url(
        AVATARS_HOST, group_id2, image_name2,
    )

    assert response.status_code == 200
    assert avatars_mds_mock.put_unnamed_handler.has_calls


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_bank_applications_db_1_2(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_agreements_mock,
        pgsql,
):
    # first page
    application_id = '11111111-1111-1111-1111-111111111111'
    image_blob = b'image jpeg 1'
    page_number1 = 'FIRST'

    image_name1 = 'auto_generated_image_name'
    group_id1 = 100

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number1,
        avatars_mds_mock,
        group_id1,
        image_name1,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')

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

    page = common.PASSPORT_PAGE_FORMAT.format(page_number1)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id1, image_name1,
    )

    assert response.status_code == 200
    assert avatars_mds_mock.put_unnamed_handler.has_calls

    # second page
    image_blob = b'image jpeg 2'
    page_number2 = 'SECOND'

    image_name2 = 'auto_generated_image_name2'
    group_id2 = 102

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number2,
        avatars_mds_mock,
        group_id2,
        image_name2,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')

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

    page = common.PASSPORT_PAGE_FORMAT.format(page_number1)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id1, image_name1,
    )

    page = common.PASSPORT_PAGE_FORMAT.format(page_number2)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id2, image_name2,
    )

    assert response.status_code == 200
    assert avatars_mds_mock.put_unnamed_handler.has_calls


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_bank_applications_db_1_2_1(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_agreements_mock,
        pgsql,
):
    # first page
    application_id = '11111111-1111-1111-1111-111111111111'
    image_blob = b'image jpeg 1'
    page_number1 = 'FIRST'

    image_name1 = 'auto_generated_image_name'
    group_id1 = 100

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number1,
        avatars_mds_mock,
        group_id1,
        image_name1,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')

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

    page = common.PASSPORT_PAGE_FORMAT.format(page_number1)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id1, image_name1,
    )

    assert response.status_code == 200
    assert avatars_mds_mock.put_unnamed_handler.has_calls

    # second page
    image_blob = b'image jpeg 2'
    page_number2 = 'SECOND'

    image_name2 = 'auto_generated_image_name2'
    group_id2 = 102

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number2,
        avatars_mds_mock,
        group_id2,
        image_name2,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')

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

    page = common.PASSPORT_PAGE_FORMAT.format(page_number1)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id1, image_name1,
    )

    page = common.PASSPORT_PAGE_FORMAT.format(page_number2)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id2, image_name2,
    )

    assert response.status_code == 200
    assert avatars_mds_mock.put_unnamed_handler.has_calls

    # first page resubmit
    image_blob = b'image jpeg 3'

    image_name3 = 'auto_generated_image_name3'
    group_id3 = 103

    data, headers = common.make_request_form(
        application_id,
        image_blob,
        page_number1,
        avatars_mds_mock,
        group_id3,
        image_name3,
    )
    headers.update(REQUIRED_HEADERS)

    pg_application_before = utils.select_application(pgsql, application_id)

    ocr_recognize_mock.set_status('success')

    response = await taxi_bank_applications.post(
        'v1/applications/v1/kyc/upload_passport', data=data, headers=headers,
    )

    pg_application_after = utils.select_application(pgsql, application_id)

    common.check_equal_without_add_params(
        pg_application_after, pg_application_before,
    )
    add_params = pg_application_after.additional_params

    page = common.PASSPORT_PAGE_FORMAT.format(page_number1)
    assert page in add_params
    assert len(add_params[page]) == 2
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id1, image_name1,
    )
    assert add_params[page][1] == common.get_image_url(
        AVATARS_HOST, group_id3, image_name3,
    )

    page = common.PASSPORT_PAGE_FORMAT.format(page_number2)
    assert page in add_params
    assert len(add_params[page]) == 1
    assert add_params[page][0] == common.get_image_url(
        AVATARS_HOST, group_id2, image_name2,
    )

    assert response.status_code == 200
    assert avatars_mds_mock.put_unnamed_handler.has_calls


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=AVATARS_HOST)
async def test_kyc_upload_passport_bank_applications_db_add_info_1(
        taxi_bank_applications,
        mockserver,
        avatars_mds_mock,
        ocr_recognize_mock,
        bank_agreements_mock,
        pgsql,
):
    application_id = '11111111-1111-1111-1111-222222222222'
    image_blob = b'image jpeg 1'
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

    ocr_recognize_mock.set_status('success')

    pg_application_before = utils.select_application(pgsql, application_id)

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
    add_params.pop(page)
    assert pg_application_before.additional_params == add_params

    assert response.status_code == 200
    assert avatars_mds_mock.put_unnamed_handler.has_calls
