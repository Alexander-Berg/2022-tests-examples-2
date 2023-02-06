import datetime
from mouse import Mouse


class TopicModel(Mouse):
    @classmethod
    def columns(cls):
        return cls.meta.fields.keys()

    @staticmethod
    def table_alias():
        return ''

    @classmethod
    def drop_query(cls):
        return f'''
            DROP TABLE IF EXISTS `{cls.table_alias()}`
        '''

    @classmethod
    def create_query(cls):
        return f'''
        CREATE TABLE IF NOT EXISTS `{cls.table_alias()}` (
            "timestamp"     DateTime('UTC') NOT NULL,
            "depot_id"      TEXT NOT NULL
        ) ENGINE = MergeTree()
        ORDER BY ("timestamp")
    '''

    def insert_query(self):
        return self.insert_query_list([self])

    @classmethod
    def insert_query_list(cls, models):
        cols = cls.meta.fields.keys()
        cols_str = ', '.join([f'"{col}"' for col in cols])
        query = f'''
            INSERT INTO `{cls.table_alias()}` ({cols_str})
            VALUES
        '''
        values_list = []
        for row in models:
            values = []
            for col in cols:
                value = getattr(row, col)
                if value is None:
                    values.append('NULL')
                elif isinstance(value, datetime.datetime):
                    values.append(f'{int(value.timestamp())}')
                else:
                    values.append(f'\'{value}\'')

            values_str = ', '.join(values)
            values_list.append(f'({values_str})')

        query += ',\n'.join(values_list)
        return query


