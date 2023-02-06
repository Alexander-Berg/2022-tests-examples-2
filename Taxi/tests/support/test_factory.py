from ciso8601 import parse_datetime_as_naive

from projects.support.factory import SupportFactory


def test_factory_create_methods(load_json):
    factory = SupportFactory(
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-05T00:00:00Z'),
        resources_dir='projects/tests/support/static/test_factory',
        preprocessor_load='drivers_support',
        data_splitter_params={
            'field': 'creation_dttm',
            'test_threshold': '2020-02-10T00:00:00Z',
            'val_threshold': '2020-02-17T00:00:00Z',
            'comparator': (
                'projects.support.data_splitters.'
                'comparators.str_dttm_comparator'
            ),
        },
    )

    factory.create_data_splitter_train_test()
    factory.create_data_splitter_train_val()
