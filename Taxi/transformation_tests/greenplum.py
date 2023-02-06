import pandas as pd

from business_models import greenplum
from business_models.transformation.greenplum import period_snapshot, SALT


def toy_loader_tests():
    """
    Пример использования функции.
    """
    schema_name = 'snb_taxi'
    target_data_table_name = 'test_period_snapshot_{}_current'.format(SALT)
    increment_data_table_name = 'test_period_snapshot_{}_increment'.format(SALT)
    try:
        current_df = pd.DataFrame(data={
            'utc_snp_dt': ['2022-02-03', '2022-02-04', '2022-02-05', '2022-02-06'],
            'unique_driver_id': ['Первый', 'Второй', 'Третий', 'Четвертый'],
            'order_cnt': [10, 20, 30, 40]
        })
        greenplum.write(current_df, '{}.{}'.format(schema_name, target_data_table_name))

        increment_df = pd.DataFrame(data={
            'utc_snp_dt': ['2022-02-04', '2022-02-05'],
            'unique_driver_id': ['Второй', 'Пятый'],
            'order_cnt': [21, 50]
        })
        greenplum.write(increment_df, '{}.{}'.format(schema_name, increment_data_table_name))

        query = """create table {{schema_name}}.{{buffer_table_name}} as
            select utc_snp_dt, unique_driver_id, order_cnt
            from {}.{}
        """.format(schema_name, increment_data_table_name)

        period_snapshot(
            table_name=target_data_table_name,
            partition_field_name='utc_snp_dt',
            start_dt='2022-02-04',
            end_dt='2022-02-05',
            query=query,
        )

        actual_result_df = greenplum \
            .read('{}.{}'.format(schema_name, target_data_table_name)) \
            .sort_values(by=['utc_snp_dt']) \
            .reset_index(drop=True)
        expected_result_df = pd.DataFrame(data={
            'utc_snp_dt': ['2022-02-03', '2022-02-04', '2022-02-05', '2022-02-06'],
            'unique_driver_id': ['Первый', 'Второй', 'Пятый', 'Четвертый'],
            'order_cnt': [10, 21, 50, 40]
        })
        assert actual_result_df.equals(expected_result_df), ("\nactual:\n{}\nexpected:\n{}".format(actual_result_df, expected_result_df))
    finally:
        greenplum('drop table if exists {}.{}'.format(schema_name, target_data_table_name))
        greenplum('drop table if exists {}.{}'.format(schema_name, increment_data_table_name))


def toy_loader_w_optional_args_tests():
    """
    Пример использования опциональных аргументов функции.
    """
    schema_name = 'snb_taxi'
    target_data_table_name = 'test_period_snapshot_{}_current'.format(SALT)
    increment_data_table_name = 'test_period_snapshot_{}_increment'.format(SALT)
    try:
        current_df = pd.DataFrame(data={
            'utc_order_dttm': ['2022-02-03 12:00:00', '2022-02-04 00:00:00', '2022-02-05 23:59:59', '2022-02-06 12:30:00'],
            'order_id': ['Первый', 'Второй', 'Третий', 'Четвертый'],
            'order_cost': [10, 20, 30, 40]
        })
        greenplum.write(current_df, '{}.{}'.format(schema_name, target_data_table_name))

        for increment_dt, increment_data in (
            (
                '2022-02-04', {
                    'utc_order_dttm': ['2022-02-04 08:30:00'],
                    'order_id': ['Второй'],
                    'order_cost': [21]
                }
            ),
            (
                '2022-02-05', {
                    'utc_order_dttm': ['2022-02-05 12:20:00'],
                    'order_id': ['Пятый'],
                    'order_cost': [50]
                }
            ),
        ):
            increment_df = pd.DataFrame(data=increment_data)
            greenplum.write(increment_df, '{}.{}'.format(schema_name, increment_data_table_name), if_exists='replace')

            query = """create table {{schema_name}}.{{buffer_table_name}} as
                select utc_order_dttm, order_id, order_cost
                from {}.{}
            """.format(schema_name, increment_data_table_name)

            period_snapshot(
                table_name=target_data_table_name,
                partition_field_name='utc_order_dttm',
                partition_field_type='datetime',
                start_dt=increment_dt,
                end_dt=increment_dt,
                query=query,
                distributed_by='order_id',
                select_grant_list=['robot-taxi-stat'],
                all_grant_list=['robot-sql-retention'],
            )

        actual_result_df = greenplum \
            .read('{}.{}'.format(schema_name, target_data_table_name)) \
            .sort_values(by=['utc_order_dttm']) \
            .reset_index(drop=True)
        expected_result_df = pd.DataFrame(data={
            'utc_order_dttm': ['2022-02-03 12:00:00', '2022-02-04 08:30:00', '2022-02-05 12:20:00', '2022-02-06 12:30:00'],
            'order_id': ['Первый', 'Второй', 'Пятый', 'Четвертый'],
            'order_cost': [10, 21, 50, 40]
        })
        assert actual_result_df.equals(expected_result_df), ("\nactual:\n{}\nexpected:\n{}".format(actual_result_df, expected_result_df))
    finally:
        greenplum('drop table if exists {}.{}'.format(schema_name, target_data_table_name))
        greenplum('drop table if exists {}.{}'.format(schema_name, increment_data_table_name))


if __name__ == "__main__":
    toy_loader_tests()
    toy_loader_w_optional_args_tests()
    print("Everything passed")
