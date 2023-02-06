import functools
import json

import pytest


def dms_decorator(
        func=None, driver_points_values={}, fallback_activity_value=100,
):
    if func is None:
        return lambda func_: dms_decorator(
            func_, driver_points_values, fallback_activity_value,
        )

    assert isinstance(driver_points_values, list) or isinstance(
        driver_points_values, dict,
    )

    @pytest.mark.parametrize('use_dms_driver_points', (True, False))
    @functools.wraps(func)
    def wrapper(
            *args,
            config,
            dms_context,
            dms_fixture,
            use_dms_driver_points,
            **kwargs,
    ):
        config.set_values(
            {
                'DMS_ACTIVITY_VALUES_ENABLED': use_dms_driver_points,
                'DRIVER_METRICS_STORAGE_CLIENT_FALLBACK_ACTIVITY_VALUE': (
                    fallback_activity_value
                ),
            },
        )
        dms_context.set_expect_dms_called(use_dms_driver_points)
        dms_context.set_use_dms_driver_points(use_dms_driver_points)
        if use_dms_driver_points:
            dms_context.set_response_driver_points(driver_points_values)

        func(
            *args,
            config=config,
            dms_fixture=dms_fixture,
            dms_context=dms_context,
            use_dms_driver_points=use_dms_driver_points,
            **kwargs,
        )

        assert (
            bool(dms_fixture.v2_activity_values_list.times_called)
            == dms_context.expect_dms_called
        ), (
            'Times called: {}, but expect_dms_called is {}'.format(
                dms_fixture.v2_activity_values_list.times_called,
                dms_context.expect_dms_called,
            )
        )

    return wrapper


def sv_proxy_decorator(
        sv_func=None,
        experiment_name='',
        consumer='',
        url='',
        result='',
        expected_args=None,
        expected_request=None,
        expected_headers=None,
):

    if sv_func is None:
        return lambda func_: sv_proxy_decorator(
            func_,
            experiment_name,
            consumer,
            url,
            result,
            expected_args,
            expected_request,
            expected_headers,
        )

    @pytest.mark.parametrize('proxy_mode', ('no_proxy', 'compare', 'proxy'))
    @functools.wraps(sv_func)
    def sv_wrapper(
            *args, load_json, mockserver, experiments3, proxy_mode, **kwargs,
    ):
        @mockserver.json_handler(url)
        def _mock_sv(sv_request):
            assert proxy_mode != 'no_proxy'

            if expected_args:
                assert sv_request.args.to_dict(flat=True) == expected_args

            if expected_request:
                request_json = json.loads(sv_request.get_data())
                assert request_json == expected_request

            if expected_headers:
                for key, value in expected_headers.items():
                    assert key in sv_request.headers
                    assert sv_request.headers[key] == value

            return load_json(result)

        experiments3.add_experiment(
            match={
                'consumers': [{'name': consumer}],
                'predicate': {
                    'init': {
                        'salt': 'salt',
                        'divisor': 100,
                        'arg_name': 'driver_profile_id',
                        'range_to': 100,
                        'range_from': 0,
                    },
                    'type': 'mod_sha1_with_salt',
                },
                'applications': [{'name': 'taximeter', 'version_range': {}}],
                'enabled': True,
            },
            name=experiment_name,
            consumers=[consumer],
            clauses=[
                {
                    'title': 'a',
                    'predicate': {'type': 'true'},
                    'value': {'mode': proxy_mode},
                },
            ],
        )

        sv_func(
            *args,
            load_json=load_json,
            mockserver=mockserver,
            experiments3=experiments3,
            proxy_mode=proxy_mode,
            **kwargs,
        )

        if proxy_mode != 'no_proxy':
            assert bool(_mock_sv.times_called) == 1
        else:
            assert bool(_mock_sv.times_called) == 0

    return sv_wrapper
