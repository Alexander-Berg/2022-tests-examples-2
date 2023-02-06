from taxi_billing_replication import billing


async def test_billing_error(billing_replictaion_cron_app):
    """
    Check for TAXIINTERNAL-234, which fixes an error with a billing failure on
    a list argument. This is an only slightly more generalized version of
    testing exactly that, opting to check all argument types seen in the
    replication process.
    """

    def fake_reformat(*args, **kwargs):
        raise ValueError

    async def fake_make_request(
            list_arg, str_arg, int_arg, additional_arg, log_extra=None,
    ):
        if int_arg == 1:
            raise ValueError

        return [{'response': 1}, {'response': 2}]

    billing_kwargs_list = [
        {'list_arg': [1, 2, 3], 'str_arg': 'arg', 'int_arg': 1},
        {'list_arg': [5, 6], 'str_arg': 'arg', 'int_arg': 13},
    ]

    _, successes, fails = await billing.perform_requests_in_bulk(
        db=billing_replictaion_cron_app.db,
        task_name='some_task',
        request_func=fake_make_request,
        additional_args={'additional_arg': 'additional'},
        billing_kwargs_list=billing_kwargs_list,
        reformat_func=fake_reformat,
        log_extra=None,
    )

    assert successes == []
    assert len(fails) == len(billing_kwargs_list)
    for billing_kwargs in billing_kwargs_list:
        assert billing_kwargs in fails
