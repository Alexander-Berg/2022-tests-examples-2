from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from noc.traffic.dns.safedns.dnsl3r.dnsl3r import cli, server


def test_cli_invalid_ips():
    result = CliRunner().invoke(cli.cli, ["-S", "0.0.0.0", "-P", "80", "192.0.2.222", "192.0.55"])
    assert result.exit_code == 1
    assert result.output == "At least some of given addresses invalid\n"


def test_cli_invalid_dn():
    result = CliRunner().invoke(cli.cli, ["--query-dn", "..", "-S", "0.0.0.0", "-P", "80", "192.0.2.222", "192.0.2.55"])
    assert result.exit_code == 2
    assert "Invalid domain name to resolve" in result.output


def test_start_server():
    server_mock = MagicMock()
    patcher2 = patch("noc.traffic.dns.safedns.dnsl3r.dnsl3r.server.sanic.Sanic", return_value=server_mock)
    patcher2.start()
    result = CliRunner().invoke(
        cli.cli, ["--query-dn", "$self", "-S", "any", "-P", "80", "2001:db8:ffff::1", "192.0.2.222"]
    )
    patcher2.stop()
    assert result.exit_code == 0
    assert server_mock.add_route.call_count == 4
    server_mock.run.assert_called_with(host="*", port=80, access_log=False)
    assert len(server_mock.ctx.counters) == 2
    assert "2001:db8:ffff::1" in server_mock.ctx.counters
    assert server.STOP_FILE in server_mock.ctx.stop_file


def test_start_server_more_params():
    server_mock = MagicMock()
    patcher2 = patch("noc.traffic.dns.safedns.dnsl3r.dnsl3r.server.sanic.Sanic", return_value=server_mock)
    patcher2.start()
    result = CliRunner().invoke(
        cli.cli,
        [
            "--query-dn",
            "query.test",
            "--query-timeout",
            "2.5",
            "--query-period",
            "6.0",
            "--rr-type",
            "A",
            "--server-logs",
            "-S",
            "::",
            "-P",
            "80",
            "2001:db8:ffff::1",
            "192.0.2.222",
        ],
    )
    patcher2.stop()
    assert result.exit_code == 0
    assert server_mock.add_route.call_count == 4
    server_mock.run.assert_called_with(host="::", port=80, access_log=False)
    # middlewares called as decorators (twice per middleware)
    assert len(server_mock.middleware.mock_calls) == 4
    assert len(server_mock.ctx.counters) == 2
    assert "192.0.2.222" in server_mock.ctx.counters
    assert server.STOP_FILE in server_mock.ctx.stop_file
