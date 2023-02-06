from dmp_suite.task.source import DataAccessor, TransformingDataAccessor


def test_transforming_data_accessor():
    class SomeData(DataAccessor):
        def get_data(self):
            yield {'first': 'Василий', 'last': 'Иванов'}
            yield {'first': 'Иван', 'last': 'Петров'}
            yield {'first': 'Мария', 'last': 'Лукина'}

    def add_full_name(item):
        new_item = item.copy()
        new_item['full_name'] = '{} {}'.format(item['first'], item['last'])
        return new_item

    def add_full_names(items):
        return list(map(add_full_name, items))

    data = SomeData()

    new_data = TransformingDataAccessor(
        data,
        add_full_names,
    )
    result = list(new_data.get_data())

    assert result[0]['full_name'] == 'Василий Иванов'
    assert result[1]['full_name'] == 'Иван Петров'
    assert result[2]['full_name'] == 'Мария Лукина'
