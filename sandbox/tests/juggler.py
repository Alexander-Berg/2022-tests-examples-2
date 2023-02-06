import six

import sandbox.deploy.juggler as deploy_juggler


class TestJuggler(object):
    def test__generate(self):
        namespace = deploy_juggler.registry.get(deploy_juggler.PRODUCTION_KEY)
        check_services = set()
        for check in namespace.get_checks():
            check_services.add(check["service"])
            six.print_(check)

        assert "active_writers" in check_services
        assert "age" in check_services
        assert "broken" in check_services
        assert "check_skynet" in check_services
        assert "consistency" in check_services
        assert "cpu" in check_services
        assert "cpu_load" in check_services
        assert "dead" in check_services
        assert "down" in check_services
        assert "errata_updates" in check_services
        assert "exception_count" in check_services
        assert "fileserver" in check_services
        assert "http" in check_services
        assert "http_errors" in check_services
        assert "http_ok" in check_services
        assert "https" in check_services
        assert "hw_errs" in check_services
        assert "limit_exceeded" in check_services
        assert "mds_cleaner" in check_services
        assert "META" in check_services
        assert "ntp_stratum" in check_services
        assert "ops_duration" in check_services
        assert "raid" in check_services
        assert "requests_in_progress" in check_services
        assert "requests_rejected" in check_services
        assert "session_consistency" in check_services
        assert "ssh" in check_services
        assert "step_clock_event" in check_services
        assert "task_wakeup_duration_multislot" in check_services
        assert "transient_statuses" in check_services
        assert "unavailable" in check_services
        assert "unispace" in check_services
        assert "UNREACHABLE" in check_services
        assert "UNREACHABLE_DISASTER" in check_services
        assert "unreplied_message" in check_services
        assert "workers_busy" in check_services
        assert "yabs_ytstat" in check_services
        assert "zookeeper" in check_services
        assert "zookeeper_mntr" in check_services

    def test_generate_preprod(self):
        namespace = deploy_juggler.registry.get(1)
        check_services = set()
        for check in namespace.get_checks():
            check_services.add(check["service"])
            six.print_(check)

        assert "dead" in check_services
        assert "down" in check_services
        assert "unispace" in check_services
        assert "UNREACHABLE" in check_services
