INVITES_DB_NAME = 'invites'


class InvitesDb:
    def __init__(self, db_cursor):
        self.db_cursor = db_cursor

    def _query_columns(self):
        return [desc[0] for desc in self.db_cursor.description]

    def get_invite_code(self, code):
        self.db_cursor.execute(
            f"""
            SELECT
                c.code,
                c.created_at,
                c.activated_at,
                m.phone_id AS consumer_phone_id,
                cl.name AS club_name
            FROM invites.codes c
            LEFT JOIN invites.members m ON m.id = c.consumer_id
            LEFT JOIN invites.clubs cl ON cl.id = m.club_id
            WHERE
                c.code = '{code}'
        """,
        )
        columns = self._query_columns()
        rows = list(self.db_cursor)
        assert len(rows) <= 1
        return dict(zip(columns, rows[0])) if rows else None

    def invite_code_exists(self, code):
        return self.get_invite_code(code) is not None

    def invite_code_is_used(self, code, phone_id=None):
        """ Check that a valid invite code is already used.

        If phone_id is passed then checks that code is used by this phone_id,
        else checks that code is used by anyone.
        """
        invite_code = self.get_invite_code(code)
        assert invite_code

        if phone_id is None:
            is_used = invite_code['consumer_phone_id'] is not None
        else:
            is_used = invite_code['consumer_phone_id'] == phone_id

        if is_used:
            assert invite_code['activated_at'] is not None
        return is_used

    def user_is_club_member(self, phone_id, club_name):
        self.db_cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM invites.members m
            JOIN invites.clubs c ON c.id = m.club_id
            WHERE
                m.phone_id = '{phone_id}' AND
                c.name = '{club_name}'
        """,
        )
        row_count = self.db_cursor.fetchone()[0]
        assert row_count <= 1
        return row_count == 1

    def get_user_invite_codes(self, club_name, phone_id):
        self.db_cursor.execute(
            f"""
            SELECT
                c.code
            FROM invites.codes c
            JOIN invites.members m ON m.id = c.creator_id
            JOIN invites.clubs cl ON cl.id = m.club_id
            WHERE
                m.phone_id = '{phone_id}' AND
                cl.name = '{club_name}'
        """,
        )
        columns = self._query_columns()
        rows = list(self.db_cursor)
        return [dict(zip(columns, row)) for row in rows]

    def club_exists(self, club_name):
        self.db_cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM invites.clubs
            WHERE
                clubs.name = '{club_name}'
        """,
        )
        rows_count = self.db_cursor.fetchone()[0]
        return rows_count == 1

    def get_club_id(self, club_name):
        self.db_cursor.execute(
            f"""
            SELECT id
            FROM invites.clubs
            WHERE
                clubs.name = '{club_name}'
        """,
        )
        club_id = self.db_cursor.fetchone()[0]
        return club_id
