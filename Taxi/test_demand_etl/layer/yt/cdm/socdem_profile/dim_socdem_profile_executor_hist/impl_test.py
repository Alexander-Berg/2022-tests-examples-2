from demand_etl.layer.yt.cdm.socdem_profile.dim_socdem_profile_executor_hist.impl import month_list


def test_month_list():
    assert month_list(b'2021-05-06', b'2021-06-08', b'2021-07-02') == [b'2021-05-01']
    assert month_list(b'2021-05-06', b'9999-12-31', b'2021-07-02') == [b'2021-07-01', b'2021-05-01', b'2021-06-01']
    assert month_list(b'2021-01-22', b'9999-12-31', b'2021-07-02') == [b'2021-07-01', b'2021-01-01', b'2021-02-01',
                                                                       b'2021-03-01', b'2021-04-01', b'2021-05-01',
                                                                       b'2021-06-01']
    assert month_list(b'2021-01-22', b'2021-01-23', b'2021-07-02') == []
    assert month_list(b'2021-01-22', b'2021-05-23', b'2021-07-02') == [b'2021-01-01', b'2021-02-01', b'2021-03-01',
                                                                       b'2021-04-01']
    assert month_list(b'2021-01-22', b'2021-07-01', b'2021-07-02') == [b'2021-01-01', b'2021-02-01', b'2021-03-01',
                                                                       b'2021-04-01', b'2021-05-01', b'2021-06-01']
