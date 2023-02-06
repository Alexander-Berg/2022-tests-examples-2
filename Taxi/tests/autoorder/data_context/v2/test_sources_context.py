from projects.autoorder.data_context.v2.sources_context import dt_2_timestamp


def test_dt_2_timestamp():
    assert (
        dt_2_timestamp(
            '2022-03-15 00:00:00', timezone='utc', format='%Y-%m-%d %H:%M:%S',
        )
        == 1647302400
    )

    assert (
        dt_2_timestamp(
            '2022-03-15', timezone='Europe/Moscow', format='%Y-%m-%d',
        )
        == 1647291600
    )


if __name__ == '__main__':
    test_dt_2_timestamp()
