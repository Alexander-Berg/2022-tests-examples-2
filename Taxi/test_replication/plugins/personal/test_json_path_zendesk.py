import pytest

from replication.plugins.personal.models import json_path_zendesk


@pytest.mark.parametrize(
    'doc, path, fail, expected_field',
    [
        ({'key1': 'find_me'}, 'key1', True, 'find_me'),
        ({'key1': {'key2': 'find_me'}}, 'key1.key2', True, 'find_me'),
        ({'key1': [{'key2': 'find_me'}]}, 'key1[*].key2', False, 'find_me'),
        (
            {'key1': [{'key2': 'find_me'}, {'key3': 'ignore_me'}]},
            'key1[*].key2',
            False,
            'find_me',
        ),
        (
            {
                'key1': [{'key2': 'find_me'}, {'key3': 'ignore_me'}],
                'key2': [{'key2': 'ignore_me'}, {'key3': 'ignore_me'}],
            },
            'key1[*].key2',
            False,
            'find_me',
        ),
        (
            {
                'key1': [
                    {'key2': [{'key3': 'find_me'}, {'key4': 'ignore_me'}]},
                    {'key3': 'ignore_me'},
                ],
            },
            'key1[*].key2[*].key3',
            False,
            'find_me',
        ),
        (
            {
                'key1': [
                    {
                        'key2': [
                            {'key3': 'find_me'},
                            {'key3': 'ignore_me'},
                            {'key4': 'ignore_me'},
                        ],
                    },
                    {'key3': 'ignore_me'},
                ],
            },
            'key1[*].key2[*].key3',
            False,
            'find_me',
        ),
        (
            {
                'child_events': [
                    {'attachments': [1, 2, 3], 'audit_id': 733476251800},
                    {'custom_ticket_fields': {'114102317274': 'TELEPHONE'}},
                ],
                'custom_ticket_fields': {'360012002014': 'TELEPHONE2'},
            },
            'child_events[*].custom_ticket_fields.\"114102317274\"',
            False,
            'TELEPHONE',
        ),
    ],
)
def test_json_path_zendesk_get_field(doc, path, fail, expected_field):
    assert json_path_zendesk.get_field(doc, path, fail) == expected_field


@pytest.mark.parametrize(
    'doc, path, fail, expected_field',
    [
        ({}, 'custom_fields[*].id.314.value', False, None),
        (
            {'custom_fields': None},
            'custom_fields[*].id.314.value',
            False,
            None,
        ),
        ({'custom_fields': []}, 'custom_fields[*].id.314.value', False, None),
        (
            {'custom_fields': [{}]},
            'custom_fields[*].id.314.value',
            False,
            None,
        ),
        (
            {'custom_fields': [{'id': 315, 'value': 'ignore_me'}]},
            'custom_fields[*].id.314.value',
            False,
            None,
        ),
        (
            {'custom_fields': [{'id': 314, 'value': 'find_me'}]},
            'custom_fields[*].id.314.value',
            True,
            'find_me',
        ),
        (
            {
                'custom_fields': [{'id': 314, 'value': 'find_me'}],
                'other_fields': [{'id': 314, 'value': 'ignore_me'}],
            },
            'custom_fields[*].id.314.value',
            True,
            'find_me',
        ),
        (
            {
                'custom_fields': [
                    {'id': 314, 'value': 'find_me'},
                    {'id': 315, 'value': 'ignore_me'},
                ],
            },
            'custom_fields[*].id.314.value',
            True,
            'find_me',
        ),
        (
            {
                'custom_fields': [
                    {
                        'id': 314,
                        'value': 'find_me',
                        'some_other_value': 'ignore_me',
                    },
                    {'id': 314, 'incorrect_value': 'ignore_me'},
                    {},
                    {'not_id': 'ignore_me'},
                    {'value': 'ignore_me'},
                ],
            },
            'custom_fields[*].id.314.value',
            True,
            'find_me',
        ),
        (
            {
                'outer_custom_fields': [
                    {
                        'custom_fields': [
                            {
                                'id': 314,
                                'value': 'find_me',
                                'some_other_value': 'ignore_me',
                            },
                            {'id': 314, 'incorrect_value': 'ignore_me'},
                            {},
                            {'not_id': 'ignore_me'},
                            {'value': 'ignore_me'},
                        ],
                    },
                ],
            },
            'outer_custom_fields[*].custom_fields[*].id.314.value',
            True,
            'find_me',
        ),
    ],
)
def test_json_path_zendesk_get_field_by_id_value(
        doc, path, fail, expected_field,
):
    assert (
        json_path_zendesk.get_field_by_id_value(doc, path, fail)
        == expected_field
    )


@pytest.mark.parametrize(
    'doc, path, value, expected_doc',
    [
        ({'key1': 'old_value'}, 'key1', 'new_value', {'key1': 'new_value'}),
        (
            {'key1': {'key2': 'old_value'}},
            'key1.key2',
            'new_value',
            {'key1': {'key2': 'new_value'}},
        ),
        (
            {'key1': [{'key2': 'old_value'}]},
            'key1[*].key2',
            'new_value',
            {'key1': [{'key2': 'new_value'}]},
        ),
        (
            {'key1': [{'key2': 'old_value'}, {'key3': 'ignore_me'}]},
            'key1[*].key2',
            'new_value',
            {'key1': [{'key2': 'new_value'}, {'key3': 'ignore_me'}]},
        ),
        (
            {
                'key1': [{'key2': 'old_value'}, {'key3': 'ignore_me'}],
                'key2': [{'key2': 'ignore_me'}, {'key3': 'ignore_me'}],
            },
            'key1[*].key2',
            'new_value',
            {
                'key1': [{'key2': 'new_value'}, {'key3': 'ignore_me'}],
                'key2': [{'key2': 'ignore_me'}, {'key3': 'ignore_me'}],
            },
        ),
        (
            {
                'key1': [
                    {'key2': [{'key3': 'old_value'}, {'key4': 'ignore_me'}]},
                    {'key3': 'ignore_me'},
                ],
            },
            'key1[*].key2[*].key3',
            'new_value',
            {
                'key1': [
                    {'key2': [{'key3': 'new_value'}, {'key4': 'ignore_me'}]},
                    {'key3': 'ignore_me'},
                ],
            },
        ),
        (
            {
                'key1': [
                    {
                        'key2': [
                            {'key3': 'old_value'},
                            {'key3': 'old_value_too'},
                            {'key4': 'ignore_me'},
                        ],
                    },
                    {'key3': 'ignore_me'},
                ],
            },
            'key1[*].key2[*].key3',
            'new_value',
            {
                'key1': [
                    {
                        'key2': [
                            {'key3': 'new_value'},
                            {'key3': 'new_value'},
                            {'key4': 'ignore_me'},
                        ],
                    },
                    {'key3': 'ignore_me'},
                ],
            },
        ),
        (
            {
                'child_events': [
                    {'attachments': [1, 2, 3], 'audit_id': 733476251800},
                    {'custom_ticket_fields': {'114102317274': 'old_value'}},
                ],
                'custom_ticket_fields': {'360012002014': 'TELEPHONE2'},
            },
            'child_events[*].custom_ticket_fields.\"114102317274\"',
            'new_value',
            {
                'child_events': [
                    {'attachments': [1, 2, 3], 'audit_id': 733476251800},
                    {'custom_ticket_fields': {'114102317274': 'new_value'}},
                ],
                'custom_ticket_fields': {'360012002014': 'TELEPHONE2'},
            },
        ),
    ],
)
def test_json_path_zendesk_set_field(doc, path, value, expected_doc):
    json_path_zendesk.set_field(doc, path, value)
    assert doc == expected_doc


@pytest.mark.parametrize(
    'doc, path, value, expected_doc',
    [
        ({}, 'custom_fields[*].id.314.value', 'new_value', {}),
        (
            {'custom_fields': None},
            'custom_fields[*].id.314.value',
            'new_value',
            {'custom_fields': None},
        ),
        (
            {'custom_fields': []},
            'custom_fields[*].id.314.value',
            'new_value',
            {'custom_fields': []},
        ),
        (
            {'custom_fields': [{}]},
            'custom_fields[*].id.314.value',
            'new_value',
            {'custom_fields': [{}]},
        ),
        (
            {'custom_fields': [{'id': 315, 'value': 'ignore_me'}]},
            'custom_fields[*].id.314.value',
            'new_value',
            {'custom_fields': [{'id': 315, 'value': 'ignore_me'}]},
        ),
        (
            {'custom_fields': [{'id': 314, 'value': 'find_me'}]},
            'custom_fields[*].id.314.value',
            'new_value',
            {'custom_fields': [{'id': 314, 'value': 'new_value'}]},
        ),
        (
            {
                'custom_fields': [{'id': 314, 'value': 'find_me'}],
                'other_fields': [{'id': 314, 'value': 'ignore_me'}],
            },
            'custom_fields[*].id.314.value',
            'new_value',
            {
                'custom_fields': [{'id': 314, 'value': 'new_value'}],
                'other_fields': [{'id': 314, 'value': 'ignore_me'}],
            },
        ),
        (
            {
                'custom_fields': [
                    {'id': 314, 'value': 'find_me'},
                    {'id': 315, 'value': 'ignore_me'},
                ],
            },
            'custom_fields[*].id.314.value',
            'new_value',
            {
                'custom_fields': [
                    {'id': 314, 'value': 'new_value'},
                    {'id': 315, 'value': 'ignore_me'},
                ],
            },
        ),
        (
            {
                'custom_fields': [
                    {
                        'id': 314,
                        'value': 'find_me',
                        'some_other_value': 'ignore_me',
                    },
                    {'id': 314, 'incorrect_value': 'ignore_me'},
                    {},
                    {'not_id': 'ignore_me'},
                    {'value': 'ignore_me'},
                ],
            },
            'custom_fields[*].id.314.value',
            'new_value',
            {
                'custom_fields': [
                    {
                        'id': 314,
                        'value': 'new_value',
                        'some_other_value': 'ignore_me',
                    },
                    {'id': 314, 'incorrect_value': 'ignore_me'},
                    {},
                    {'not_id': 'ignore_me'},
                    {'value': 'ignore_me'},
                ],
            },
        ),
    ],
)
def test_json_path_zendesk_set_field_by_id_value(
        doc, path, value, expected_doc,
):
    json_path_zendesk.set_field_by_id_value(doc, path, value)
    assert doc == expected_doc


@pytest.mark.parametrize(
    'doc, path', [(None, None), ({}, None), ('', None), ({}, ''), ('', '')],
)
def test_json_path_zendesk_get_field_exception(doc, path):
    with pytest.raises(json_path_zendesk.ImproperArguments):
        json_path_zendesk.get_field(doc, path)
        json_path_zendesk.get_field_by_id_value(doc, path)


@pytest.mark.parametrize(
    'doc, path, value',
    [(None, None, None), ({}, '', None), ({}, '', ''), ({}, '', {})],
)
def test_json_path_zendesk_set_field_exception(doc, path, value):
    with pytest.raises(json_path_zendesk.ImproperArguments):
        json_path_zendesk.set_field(doc, path, value)
        json_path_zendesk.get_field_by_id_value(doc, path, value)
