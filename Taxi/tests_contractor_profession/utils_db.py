PROFESSION_FIELDS = ['increment', 'park_id', 'contractor_id', 'profession_id']

PARK_ID = 'db1'
DRIVER_ID = 'uuid1'
PROFESSION_ID = 'taxi-driver'


def insert_professions(
        pgsql, park_id=None, driver_profile_id=None, profession_id=None,
):
    cursor = pgsql['contractor_profession'].cursor()
    cursor.execute(
        'INSERT INTO contractor_profession.professions '
        '(park_id, contractor_id, profession_id) '
        'VALUES '
        f'(\'{park_id or PARK_ID}\', '
        f' \'{driver_profile_id or DRIVER_ID}\', '
        f' \'{profession_id or PROFESSION_ID}\')',
    )


def select_professions(
        pgsql,
        fields=None,
        park_id=None,
        driver_profile_id=None,
        profession_id=None,
):
    fields = fields or PROFESSION_FIELDS
    cursor = pgsql['contractor_profession'].cursor()
    cursor.execute(
        f'SELECT  {",".join(fields)} '
        'FROM contractor_profession.professions '
        f'WHERE ({park_id is None} OR park_id = \'{park_id}\') '
        f'AND ({driver_profile_id is None} '
        f'  OR contractor_id = \'{driver_profile_id}\') '
        f'AND ({profession_id is None} '
        f'  OR profession_id = \'{profession_id}\') ',
    )
    return list(cursor)


def select_professions_changelog(pgsql):
    cursor = pgsql['contractor_profession'].cursor()
    cursor.execute(
        """SELECT increment, park_id, contractor_id, profession_id, source
        FROM contractor_profession.professions_changelog
        ORDER BY increment
        """,
    )
    return list(cursor)
