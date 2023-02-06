# pylint: disable=redefined-outer-name
import pytest


@pytest.mark.parametrize(
    'status,channel,permissions,expected_status',
    [
        ('New', 'freelance', ['lead_eats_fields'], 'Created'),
        ('New', 'referral', ['lead_eats_fields'], 'Not lead'),
        ('New', 'freelance', [], 'New'),
        ('Test passed', 'freelance', ['lead_eats_fields'], 'Created'),
        ('Active', 'freelance', ['lead_eats_fields'], 'Active'),
        ('active_1', 'freelance', ['lead_eats_fields'], 'Active 1'),
        ('active_5', 'freelance', ['lead_eats_fields'], 'Active 5'),
        ('active_5', 'organic', ['lead_eats_fields'], 'Not lead'),
        ('active_10', 'freelance', ['lead_eats_fields'], 'Active'),
    ],
)
def test_lead_status_converter_get_new_status(
        library_context, status, channel, permissions, expected_status,
):
    new_status = library_context.lead_status_converter.get_new_status(
        status, channel, permissions,
    )
    assert new_status == expected_status


@pytest.mark.parametrize(
    'converted_statuses,permissions,expected_statuses',
    [
        (
            ['Active'],
            ['lead_eats_fields'],
            {'Active', 'active_10', 'active_15', 'active_50', 'active_100'},
        ),
        (
            ['Active 1', 'Active 5'],
            ['lead_eats_fields'],
            {'active_1', 'active_5'},
        ),
        (
            ['Created'],
            ['lead_eats_fields'],
            {
                'New',
                'Sent for online training',
                'Online training',
                'Test passed',
                'Invited to HUB',
            },
        ),
        ([], ['lead_eats_fields'], set()),
        (['Invalid status'], ['lead_eats_fields'], set()),
        (['Active', 'Created'], [], {'Active', 'Created'}),
        (['Active', 'Created'], ['other_permissions'], {'Active', 'Created'}),
        ([], [], set()),
    ],
)
def test_lead_status_converter_get_default_statuses(
        library_context, converted_statuses, permissions, expected_statuses,
):
    default_statuses = (
        library_context.lead_status_converter.get_default_statuses(
            converted_statuses, permissions,
        )
    )
    assert default_statuses == expected_statuses
