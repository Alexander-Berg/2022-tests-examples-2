# pylint: disable=redefined-outer-name
import psycopg2.extensions
import pytest

from eats_tips_partners.crontasks import synchronize_mysql_data
from eats_tips_partners.generated.cron import run_cron

EXISTING_PARTNERS_USER_SYNC = {
    '30': '00000000-0000-0000-0000-000000000003',
    '180': '00000000-0000-0000-0000-000000000018',
    '190': '00000000-0000-0000-0000-000000000019',
}
EXISTING_PARTNERS_ORG_SYNC = {
    '10': '00000000-0000-0000-0000-000000000001',
    '100': '00000000-0000-0000-0000-000000000010',
    '110': '00000000-0000-0000-0000-000000000011',
    '120': '00000000-0000-0000-0000-000000000012',
    '140': '00000000-0000-0000-0000-000000000014',
}
EXISTING_PARTNERS_ROLE_SYNC = {
    '10': '00000000-0000-0000-0000-000000000001',
    '30': '00000000-0000-0000-0000-000000000003',
    '100': '00000000-0000-0000-0000-000000000010',
    '110': '00000000-0000-0000-0000-000000000011',
}
EXISTING_PLACES_USER_SYNC = {'30': '10000000-0000-0000-0000-000000000003'}
EXISTING_PLACES_ORG_SYNC = {'10': '10000000-0000-0000-0000-000000000001'}
EXISTING_PLACES_ROLE_SYNC = {
    '30': '10000000-0000-0000-0000-000000000003',
    '100': '10000000-0000-0000-0000-000000000010',
}


def _get_cursor_value(cursor: psycopg2.extensions.cursor, *, slug: str) -> int:
    cursor.execute(
        f"""
            SELECT cursor
            FROM eats_tips_partners.mysql_cursor AS mc
            WHERE mc.slug = '{slug}'
            ;
        """,
    )
    return cursor.fetchone()[0]


def _set_cursor_value(
        cursor: psycopg2.extensions.cursor, *, slug: str, value: int,
):
    cursor.execute(
        f"""
            UPDATE eats_tips_partners.mysql_cursor
            SET cursor={value}
            WHERE slug='{slug}'
            ;
        """,
    )


def _get_partners(cursor: psycopg2.extensions.cursor):
    cursor.execute(
        f"""
            SELECT partner.alias, partner.id, partner.b2p_id, partner.mysql_id
            FROM eats_tips_partners.partner AS partner
            ;
        """,
    )
    return cursor.fetchall()


def _get_places(cursor: psycopg2.extensions.cursor):
    cursor.execute(
        f"""
            SELECT place.id, place.alias, place.mysql_id, place.deleted_at
            FROM eats_tips_partners.place AS place
            ;
        """,
    )
    return cursor.fetchall()


def _get_places_partners(cursor: psycopg2.extensions.cursor):
    cursor.execute(
        f"""
            SELECT
                place.mysql_id,
                partner.mysql_id,
                partner.alias,
                places_partners.roles,
                places_partners.deleted_at,
                places_partners.show_in_menu,
                places_partners.confirmed,
                places_partners.alias as pp_alias
            FROM eats_tips_partners.places_partners AS places_partners
            LEFT JOIN eats_tips_partners.place AS place
                ON place.id = places_partners.place_id
            LEFT JOIN eats_tips_partners.partner AS partner
                ON partner.id = places_partners.partner_id
            ;
        """,
    )
    return cursor.fetchall()


def _check_partners(cursor: psycopg2.extensions.cursor, *, expected, existing):
    rows = _get_partners(cursor)
    for row in rows:
        if row[0] in existing:
            assert row[1] == existing[row[0]]
    assert {(row[2], row[3]) for row in rows} == {(x, x) for x in expected}


def _check_places(cursor: psycopg2.extensions.cursor, *, expected, existing):
    rows = _get_places(cursor)
    places = set()
    for row in rows:
        places.add(row[1])
        if row[1] in existing:
            assert row[0] == existing[row[1]]
        # assert row[1] == row[2]
    assert places == expected


@pytest.fixture()
def patch_sync_new_users(patch):
    @patch(
        'eats_tips_partners.crontasks.synchronize_mysql_data'
        '.sync_new_users',
    )
    async def _sync_new_users(context, *args, **kwargs):
        return


@pytest.fixture()
def patch_sync_user_role(patch):
    @patch(
        'eats_tips_partners.crontasks.synchronize_mysql_data'
        '.sync_user_role',
    )
    async def _sync_user_role(context, *args, **kwargs):
        return


@pytest.fixture()
def patch_sync_super_admin_links(patch):
    @patch(
        'eats_tips_partners.crontasks.synchronize_mysql_data'
        '.sync_super_admin_links',
    )
    async def _sync_super_admin_links(context, *args, **kwargs):
        return


@pytest.fixture()
def patch_link_users_and_invites(patch):
    @patch(
        'eats_tips_partners.crontasks.synchronize_mysql_data'
        '.link_users_and_invites',
    )
    async def _sync_super_admin_links(context, *args, **kwargs):
        return


@pytest.mark.parametrize(
    (
        'cursor_value',
        'expected_partners',
        'expected_places',
        'expected_links',
        'expected_aliases',
        'expected_cursor',
    ),
    (
        (
            0,
            {
                '1',
                '2',
                '3',
                '4',
                '10',
                '11',
                '12',
                '13',
                '14',
                '15',
                '16',
                '17',
                '18',
                '19',
                '40',
                '50',
                '51',
                '100',
            },
            {'0000010', '0000020', '0000030', '0000040'},
            {
                # place.mysql_id, partner.mysql_id, partner.alias, roles,
                # pp.alias
                ('1', '1', None, ('admin',), None),
                ('2', '2', None, ('admin',), None),
                ('2', '100', None, ('admin',), None),
                ('3', '3', None, ('admin',), '0000030'),
                ('4', '4', None, ('admin',), None),
            },
            {
                ('0000010', 'place'),
                ('0000020', 'place'),
                ('0000030', 'place'),
                ('0000040', 'place'),
                ('0000100', 'partner'),
                ('0000110', 'partner'),
                ('0000120', 'partner'),
                ('0000130', 'partner'),
                ('0000150', 'partner'),
                ('0000160', 'partner'),
                ('0000140', 'partner'),
                ('0000170', 'partner'),
                ('0000180', 'partner'),
                ('0000190', 'partner'),
                ('0000400', 'partner'),
            },
            100,
        ),
        (
            13,
            {
                '2',
                '3',
                '14',
                '15',
                '16',
                '17',
                '18',
                '19',
                '40',
                '50',
                '51',
                '100',
            },
            {'0000020', '0000030'},
            {
                # place.mysql_id, partner.mysql_id, partner.alias, roles
                # pp.alias
                ('2', '2', None, ('admin',), None),
                ('2', '100', None, ('admin',), None),
                ('3', '3', None, ('admin',), '0000030'),
            },
            {
                ('0000020', 'place'),
                ('0000030', None),
                ('0000150', 'partner'),
                ('0000160', 'partner'),
                ('0000140', 'partner'),
                ('0000170', 'partner'),
                ('0000180', 'partner'),
                ('0000190', 'partner'),
                ('0000400', 'partner'),
            },
            100,
        ),
        (
            99999,
            {'3', '18', '19'},
            {'0000030'},
            {('3', '3', None, ('admin',), '0000030')},
            {('0000030', None), ('0000180', None), ('0000190', None)},
            99999,
        ),
    ),
)
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.pgsql('eats_tips_partners', files=['pg_base.sql'])
async def test_synchronize_new_users(
        patch_sync_user_role,
        patch_sync_super_admin_links,
        patch_link_users_and_invites,
        pgsql,
        cursor_value,
        expected_partners,
        expected_places,
        expected_links,
        expected_aliases,
        expected_cursor,
):
    cursor_slug = synchronize_mysql_data.USER_CURSOR
    cursor = pgsql['eats_tips_partners'].cursor()
    _set_cursor_value(cursor, slug=cursor_slug, value=cursor_value)

    await run_cron.main(
        ['eats_tips_partners.crontasks.synchronize_mysql_data', '-t', '0'],
    )
    _check_partners(
        cursor,
        expected=expected_partners,
        existing=EXISTING_PARTNERS_USER_SYNC,
    )
    _check_places(
        cursor, expected=expected_places, existing=EXISTING_PLACES_USER_SYNC,
    )

    partner_places = _get_places_partners(cursor)
    rows = set(
        (row[0], row[1], row[2], tuple(row[3]), row[7])
        for row in partner_places
    )
    assert rows == expected_links

    new_cursor_value = _get_cursor_value(cursor, slug=cursor_slug)
    assert new_cursor_value == expected_cursor
    cursor.execute('select alias, type from eats_tips_partners.alias')
    aliases = set(cursor.fetchall())
    assert aliases == expected_aliases


@pytest.mark.parametrize(
    (
        'cursor_value',
        'expected_partners',
        'expected_places',
        'expected_links',
        'expected_aliases',
        'expected_cursor',
    ),
    (
        (
            0,
            {'1', '3', '10', '11'},
            {'0000010', '0000030', '0000100'},
            # place.mysql_id, partner.mysql_id, partner.alias, roles
            {
                ('1', '1', None, ('admin',), False, False, True),
                ('10', '10', '0000100', ('admin',), True, False, True),
                ('10', '11', '0000110', ('recipient',), True, False, True),
                ('3', '3', None, ('admin',), False, False, True),
            },
            {
                ('0000010', 'place'),
                ('0000030', 'place'),
                ('0000100', 'partner'),
                ('0000110', 'place_partner'),
            },
            3,
        ),
        (
            1,
            {'1', '3', '10', '11'},
            {'0000030', '0000100'},
            {
                ('10', '10', '0000100', ('admin',), True, False, True),
                ('10', '11', '0000110', ('recipient',), True, False, True),
                ('3', '3', None, ('admin',), False, False, True),
            },
            {
                ('0000010', None),
                ('0000030', 'place'),
                ('0000100', 'partner'),
                ('0000110', 'place_partner'),
            },
            3,
        ),
        (
            99999,
            {'1', '3', '10', '11'},
            {'0000030', '0000100'},
            {
                ('10', '10', None, ('admin',), False, False, True),
                ('10', '11', '0000110', ('recipient',), False, False, True),
                ('3', '3', None, ('admin',), False, False, True),
            },
            {
                ('0000010', None),
                ('0000030', None),
                ('0000100', None),
                ('0000110', 'place_partner'),
            },
            99999,
        ),
    ),
)
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.pgsql('eats_tips_partners', files=['pg_base.sql'])
async def test_synchronize_user_role(
        patch_sync_new_users,
        patch_sync_super_admin_links,
        patch_link_users_and_invites,
        pgsql,
        cursor_value,
        expected_partners,
        expected_places,
        expected_links,
        expected_aliases,
        expected_cursor,
):
    cursor_slug = synchronize_mysql_data.USER_ROLE_CURSOR
    cursor = pgsql['eats_tips_partners'].cursor()
    _set_cursor_value(cursor, slug=cursor_slug, value=cursor_value)

    await run_cron.main(
        ['eats_tips_partners.crontasks.synchronize_mysql_data', '-t', '0'],
    )

    _check_partners(
        cursor,
        expected=expected_partners,
        existing=EXISTING_PARTNERS_ROLE_SYNC,
    )
    _check_places(
        cursor, expected=expected_places, existing=EXISTING_PLACES_ROLE_SYNC,
    )
    partner_places = _get_places_partners(cursor)
    rows = set(
        (
            row[0],
            row[1],
            row[2],
            tuple(row[3]),
            row[4] is not None,
            row[5],
            row[6],
        )
        for row in partner_places
    )
    assert rows == expected_links
    new_cursor_value = _get_cursor_value(cursor, slug=cursor_slug)
    assert new_cursor_value == expected_cursor
    cursor.execute('select alias, type from eats_tips_partners.alias')
    aliases = set(cursor.fetchall())
    assert aliases == expected_aliases


@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.pgsql('eats_tips_partners', files=['pg_base.sql'])
async def test_synchronize_super_admins_links(
        patch_sync_new_users, patch_sync_user_role, pgsql,
):
    await run_cron.main(
        ['eats_tips_partners.crontasks.synchronize_mysql_data', '-t', '0'],
    )

    cursor = pgsql['eats_tips_partners'].cursor()

    places_partners = _get_places_partners(cursor)
    rows = set(
        (row[0], row[1], tuple(row[3]), bool(row[4]))
        for row in places_partners
    )
    assert rows == {
        # есть и в pg и в mysql (ничего не изменилось)
        ('2', '100', ('admin',), False),
        # в pg есть, в mysql нет (удаление)
        ('2', '105', ('admin',), True),
        # в pg помечено удаленным, в mysql есть ("разудаление")
        ('2', '103', ('admin',), False),
        # в pg помечено удаленным, в mysql нет (не изменено)
        ('2', '104', ('admin',), True),
        # в pg нет, в mysql есть (создание)
        ('3', '100', ('admin',), False),
    }


@pytest.mark.config(
    TVM_RULES=[{'src': 'eats-tips-partners', 'dst': 'personal'}],
)
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.pgsql('eats_tips_partners', files=['pg_base.sql'])
async def test_link_users_and_invites(
        mockserver,
        patch_sync_new_users,
        patch_sync_user_role,
        patch_sync_super_admin_links,
        pgsql,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    async def _mock_phones_retrieve(request):
        return {'items': [{'id': 'phone_id_10', 'value': '+79000000010'}]}

    cursor = pgsql['eats_tips_partners'].cursor()
    await run_cron.main(
        ['eats_tips_partners.crontasks.synchronize_mysql_data', '-t', '0'],
    )

    cursor.execute('select * from eats_tips_partners.place_invitation;')
    for row in cursor.fetchall():
        if row[1] == 'phone_id_10':
            assert row[2] == '00000000-0000-0000-0000-000000000010'
        else:
            assert row[2] is None
