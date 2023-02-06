import pytest

REVISION_PATTERN = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla'


@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
@pytest.mark.config(
    EATS_RESTAPP_MENU_CLEAR_OLD_REVISIONS={
        'enabled': True,
        'interval': 24,
        'revisions_ttl': 24,
    },
)
async def test_clear_old_revisions_periodic_basic(
        taxi_eats_restapp_menu, pg_get_revisions, pg_get_menu_content,
):
    rev_set = set(rev['revision'] for rev in pg_get_revisions())
    expected_set = set(REVISION_PATTERN + str(val) for val in range(1, 11))
    assert rev_set == expected_set

    cont_set = tuple(
        (rev['place_id'], rev['menu_hash']) for rev in pg_get_menu_content()
    )
    expected_set = (
        (123, 'some_hash1'),
        (124, 'some_hash2'),
        (124, 'some_hash3'),
        (124, 'some_hash4'),
        (124, 'some_hash9'),
        (125, 'some_hash2'),
        (126, 'some_hash2'),
        (126, 'some_hash6'),
    )
    assert cont_set == expected_set

    await taxi_eats_restapp_menu.run_periodic_task(
        'clear-old-revisions-periodic',
    )

    rev_set = set(rev['revision'] for rev in pg_get_revisions())
    expected_set = set(REVISION_PATTERN + str(val) for val in (2, 4, 5, 10))
    assert rev_set == expected_set

    cont_set = tuple(
        (rev['place_id'], rev['menu_hash']) for rev in pg_get_menu_content()
    )
    expected_set = (
        (124, 'some_hash2'),
        (124, 'some_hash3'),
        (124, 'some_hash4'),
        (125, 'some_hash2'),
    )
    assert cont_set == expected_set
