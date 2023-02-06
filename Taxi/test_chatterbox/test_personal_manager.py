# pylint: disable=too-many-arguments, no-member, too-many-locals
import datetime

import pytest

from taxi.clients import personal

from chatterbox.internal import personal_manager

NOW = datetime.datetime(2018, 6, 7, 12, 34, 56)


@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'user_email': 'emails',
            'driver_license': 'driver_licenses',
            'driver_phone': 'phones',
            'park_phone': 'phones',
            'park_email': 'emails',
        },
    },
)
@pytest.mark.parametrize(
    ('task_id', 'metadata', 'expected_metadata'),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'user_phone': '+79999999999',
                'user_email': 'some_client@email',
                'driver_license': 'some_driver_license',
                'park_email': ['some_client@email', 'other_park@email'],
            },
            {
                'driver_license': 'some_driver_license',
                'driver_license_pd_id': 'driver_license_pd_id_1',
                'user_email': 'some_client@email',
                'user_email_pd_id': 'email_pd_id_1',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'park_email': ['some_client@email', 'other_park@email'],
                'park_email_pd_id': ['email_pd_id_1', 'test_pd_id'],
            },
        ),
        ('5b2cae5cb2682a976914c2a1', {'user_phone': ''}, {'user_phone': ''}),
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            {
                'user_phone': '+79999999999',
                'user_email': 'some_client@email',
                'driver_license': 'some_driver_license',
            },
            {
                'driver_license': 'some_driver_license',
                'user_email': 'some_client@email',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
            },
            marks=[
                pytest.mark.config(
                    CHATTERBOX_PERSONAL={
                        'enabled': True,
                        'personal_fields': {'user_phone': 'phones'},
                    },
                ),
            ],
        ),
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            {'user_phone': '+79999999999', 'some_field': 'some_value'},
            {'user_phone_pd_id': 'phone_pd_id_1', 'some_field': 'some_value'},
            marks=[
                pytest.mark.config(
                    CHATTERBOX_PERSONAL={
                        'enabled': True,
                        'personal_fields': {'user_phone': 'phones'},
                        'excluded_conditions': {'line': 'first'},
                    },
                ),
            ],
        ),
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            {'user_phone': '+79999999999', 'some_field': 'some_value'},
            {
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'some_field': 'some_value',
            },
            marks=[
                pytest.mark.config(
                    CHATTERBOX_PERSONAL={
                        'enabled': True,
                        'personal_fields': {'user_phone': 'phones'},
                        'excluded_conditions': {'line': 'second'},
                    },
                ),
            ],
        ),
    ],
)
async def test_make_personal_metadata(
        cbox, monkeypatch, mock_personal, task_id, metadata, expected_metadata,
):
    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    result = await cbox.app.personal_manager.make_personal_metadata(
        metadata, task,
    )
    assert result == expected_metadata


@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'user_email': 'emails',
            'driver_license': 'driver_licenses',
            'driver_phone': 'phones',
            'park_phone': 'phones',
            'park_email': 'emails',
        },
    },
)
@pytest.mark.parametrize(
    ('task_id', 'metadata_changes', 'expected_metadata_changes'),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_email',
                    'value': 'some_client@email',
                },
                {
                    'change_type': 'set',
                    'field_name': 'driver_license',
                    'value': 'some_driver_license',
                },
            ],
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_email',
                    'value': 'some_client@email',
                },
                {
                    'change_type': 'set',
                    'field_name': 'driver_license',
                    'value': 'some_driver_license',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_phone_pd_id',
                    'value': 'phone_pd_id_1',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_email_pd_id',
                    'value': 'email_pd_id_1',
                },
                {
                    'change_type': 'set',
                    'field_name': 'driver_license_pd_id',
                    'value': 'driver_license_pd_id_1',
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            [{'change_type': 'set', 'field_name': 'user_phone', 'value': ''}],
            [{'change_type': 'set', 'field_name': 'user_phone', 'value': ''}],
        ),
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_email',
                    'value': 'some_client@email',
                },
                {
                    'change_type': 'set',
                    'field_name': 'driver_license',
                    'value': 'some_driver_license',
                },
            ],
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_email',
                    'value': 'some_client@email',
                },
                {
                    'change_type': 'set',
                    'field_name': 'driver_license',
                    'value': 'some_driver_license',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_phone_pd_id',
                    'value': 'phone_pd_id_1',
                },
            ],
            marks=[
                pytest.mark.config(
                    CHATTERBOX_PERSONAL={
                        'enabled': True,
                        'personal_fields': {'user_phone': 'phones'},
                    },
                ),
            ],
        ),
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
            ],
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_phone_pd_id',
                    'value': 'phone_pd_id_1',
                },
            ],
            marks=[
                pytest.mark.config(
                    CHATTERBOX_PERSONAL={
                        'enabled': True,
                        'personal_fields': {'user_phone': 'phones'},
                        'excluded_conditions': {'line': 'second'},
                    },
                ),
            ],
        ),
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_phone_pd_id',
                    'value': 'phone_pd_id_1',
                },
                {'change_type': 'delete', 'field_name': 'user_email'},
                {'change_type': 'delete', 'field_name': 'user_email_pd_id'},
            ],
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_phone_pd_id',
                    'value': 'phone_pd_id_1',
                },
                {'change_type': 'delete', 'field_name': 'user_email'},
                {'change_type': 'delete', 'field_name': 'user_email_pd_id'},
            ],
            marks=[
                pytest.mark.config(
                    CHATTERBOX_PERSONAL={
                        'enabled': True,
                        'personal_fields': {'user_phone': 'phones'},
                    },
                ),
            ],
        ),
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_phone_pd_id',
                    'value': 'phone_pd_id_1_error',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_email',
                    'value': 'some_client@email',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_email_pd_id',
                    'value': 'email_pd_id_1_error',
                },
            ],
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_phone_pd_id',
                    'value': 'phone_pd_id_1',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_email',
                    'value': 'some_client@email',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_email_pd_id',
                    'value': 'email_pd_id_1',
                },
            ],
            marks=[
                pytest.mark.config(
                    CHATTERBOX_PERSONAL={
                        'enabled': True,
                        'personal_fields': {
                            'user_phone': 'phones',
                            'user_email': 'emails',
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_phone_pd_id',
                    'value': 'phone_pd_id_1',
                },
            ],
            [
                {
                    'change_type': 'set',
                    'field_name': 'user_phone_pd_id',
                    'value': 'phone_pd_id_1',
                },
            ],
            marks=[
                pytest.mark.config(
                    CHATTERBOX_PERSONAL={
                        'enabled': True,
                        'personal_fields': {'user_phone': 'phones'},
                        'excluded_conditions': {'line': 'first'},
                    },
                ),
            ],
        ),
    ],
)
async def test_make_personal_metadata_changes(
        cbox,
        monkeypatch,
        mock_personal,
        task_id,
        metadata_changes,
        expected_metadata_changes,
):
    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    result = await cbox.app.personal_manager.make_personal_metadata_changes(
        metadata_changes, task,
    )
    assert result == expected_metadata_changes


@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'user_phone': 'phones'},
        'strict_raw_query': False,
    },
)
@pytest.mark.parametrize(
    ('metadata', 'strict', 'expected_metadata', 'call_ok'),
    [
        ({'user_phone_pd_id': 'phone_pd_id_error'}, True, None, False),
        (
            {'user_phone_pd_id': 'phone_pd_id_7'},
            True,
            {
                'user_phone': 'some_user_phone',
                'user_phone_pd_id': 'phone_pd_id_7',
            },
            True,
        ),
        (
            {'user_phone_pd_id': 'phone_pd_id_error'},
            False,
            {'user_phone_pd_id': 'phone_pd_id_error'},
            True,
        ),
        (
            {'user_phone_pd_id': 'phone_pd_id_7'},
            False,
            {
                'user_phone': 'some_user_phone',
                'user_phone_pd_id': 'phone_pd_id_7',
            },
            True,
        ),
    ],
)
async def test_personal_raw_error(
        cbox,
        monkeypatch,
        mockserver,
        patch,
        load_json,
        metadata,
        strict,
        expected_metadata,
        call_ok,
):
    @patch('taxi.clients.personal.PersonalApiClient._get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {'auth': 'ticket'}

    async def mock_retrieve_item(*args, **kwargs):
        pd_data = load_json('personal_data.json')
        items = pd_data['phones']
        for item in items:
            if item['id'] == kwargs.get('request_id'):
                return item['value']
        raise personal.BaseError

    monkeypatch.setattr(
        personal.PersonalApiClient, 'retrieve_value', mock_retrieve_item,
    )

    if call_ok:
        result = await cbox.app.personal_manager.make_raw_metadata(
            metadata, strict=strict,
        )
        assert result == expected_metadata
    else:
        with pytest.raises(personal_manager.PersonalRetrieveError):
            await cbox.app.personal_manager.make_raw_metadata(
                metadata, strict=strict,
            )
