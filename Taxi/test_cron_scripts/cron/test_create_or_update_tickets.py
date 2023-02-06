import pytest

from infranaim.models.configs import external_config


def test_create_or_update_test_mode(
        get_mongo,
        run_create_or_update,
        load_binary,
        save_csv_in_project_dir,
        check_file_not_in_project_dir,
        find_documents_in_create_queue,
):
    mongo = get_mongo
    file_name = 'csv_personal_data_only.csv'
    save_csv_in_project_dir(
        load_binary(file_name),
        file_name
    )
    run_create_or_update(
        mongo,
        '--source={}'.format('/app/cron_scripts/{}'.format(file_name)),
        '--disable_countdown',
    )

    assert check_file_not_in_project_dir(file_name) == 1
    assert len(find_documents_in_create_queue(mongo)) == 0


@pytest.mark.parametrize(
    'file_name',
    ['csv_personal_data_only.csv', 'csv_personal_id_only.csv'],
)
@pytest.mark.parametrize('personal_response', ['valid', 'invalid'])
@pytest.mark.parametrize('store_personal', [1, 0])
@pytest.mark.parametrize(
    ('priority_arg', 'expected_priority'),
    [
        (None, 1),
        ('--priority=2', 2),
    ],
)
def test_create_or_update_production_mode(
        get_mongo,
        run_create_or_update,
        load_binary,
        save_csv_in_project_dir,
        check_file_not_in_project_dir,
        find_documents_in_create_queue,
        patch,
        find_field,
        personal,
        file_name,
        personal_response,
        store_personal,
        priority_arg,
        expected_priority,
):
    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})
    @patch('infranaim.clients.personal.PreparedRequestMain._generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal(personal_response, *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    mongo = get_mongo
    save_csv_in_project_dir(
        load_binary(file_name),
        file_name
    )

    args = [
        '--source={}'.format('/app/cron_scripts/{}'.format(file_name)),
        '--production',
        '--disable_countdown',
    ]
    if priority_arg is not None:
        args.append(priority_arg)

    run_create_or_update(
        mongo,
        *args,
    )

    assert check_file_not_in_project_dir(file_name) == 0

    docs = find_documents_in_create_queue(mongo)
    assert len(docs) == 1

    priority = docs[0]['priority']
    assert priority == expected_priority

    ticket = docs[0]['data']
    phone = find_field(ticket['custom_fields'], 30557445)
    pd_phone = find_field(ticket['custom_fields'], 360005536320)
    driver_license = find_field(ticket['custom_fields'], 30148269)
    pd_license = find_field(ticket['custom_fields'], 360005536340)

    if (
        (
            not store_personal
            and personal_response == 'valid'
        )
        or file_name == 'csv_personal_id_only.csv'
    ):
        assert not any([phone, driver_license])
    else:
        assert phone['value']
        assert driver_license['value']

    if (
        personal_response != 'valid'
        and file_name == 'csv_personal_data_only.csv'
    ):
        assert not any([pd_license, pd_phone])
    else:
        assert pd_phone['value']
        assert pd_license['value']
