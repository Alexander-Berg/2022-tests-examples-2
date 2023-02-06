import pytest


@pytest.fixture(autouse=False, name='db')
def mentorship_pg(pgsql):
    class Wrapper:
        @staticmethod
        def execute(sql, parameters=None):
            db = pgsql['grocery_performer_mentorship']
            cursor = db.cursor()
            cursor.execute(sql, parameters)
            return cursor

        @staticmethod
        def select_rows(sql):
            return Wrapper.execute(sql).fetchall()

        @staticmethod
        def select(keys, table):
            select_keys = ', '.join(keys)
            result = []
            for item in Wrapper.select_rows(
                    f'SELECT {select_keys}'
                    f' FROM grocery_performer_mentorship.{table}',
            ):
                push = {}
                for i, value in enumerate(item):
                    push[keys[i]] = value
                result.append(push)
            return result

        def mentorship(self, extra_fields=()):
            class Helper:
                def __init__(self):
                    self.rows = Wrapper.select(
                        (
                            'newbie_id',
                            'newbie_shift_id',
                            'mentor_id',
                            'mentor_shift_id',
                            'status',
                        )
                        + extra_fields,
                        'mentorship',
                    )

                def get(self, newbie_id):
                    for row in self.rows:
                        if row['newbie_id'] == newbie_id:
                            return row
                    return None

            return Helper()

        def check_mentorship(self, newbie_id):
            return self.mentorship().get(newbie_id)

    wrapper = Wrapper()
    return wrapper
