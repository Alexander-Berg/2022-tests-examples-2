from unittest.mock import Mock, patch

from click.testing import CliRunner

from noc.traffic.dns.safedns.dnsl3r.dnsl3r import cli


def test_cli_no_ip_list():
    result = CliRunner().invoke(cli.cli, ["-S", "0.0.0.0", "-P", "80"])
    assert result.exit_code == 0
    assert result.output == "Nothing to work on\n"


def test_cli_invalid_ips():
    with patch("noc.traffic.dns.safedns.dnsl3r.dnsl3r.cli.utils.parse_ip_list", return_value=["192.0.2.222"]):
        result = CliRunner().invoke(cli.cli, ["-S", "0.0.0.0", "-P", "80", "192.0.2.222", "192.0.55"])
    assert result.exit_code == 1
    assert result.output == "At least some of given addresses invalid\n"


def test_cli_invalid_dn():
    with patch("noc.traffic.dns.safedns.dnsl3r.dnsl3r.cli.utils.check_dn", return_value=False):
        result = CliRunner().invoke(
            cli.cli, ["--query-dn", "..", "-S", "0.0.0.0", "-P", "80", "192.0.2.222", "192.0.2.55"]
        )
    assert result.exit_code == 2
    assert "Invalid domain name to resolve" in result.output


def test_cli_invalid_port():
    result = CliRunner().invoke(cli.cli, ["-S", "0.0.0.0", "-P", "800000", "192.0.2.15"])
    assert result.exit_code == 2
    assert "Invalid value" in result.output


def test_cli_invalid_server_address():
    result = CliRunner().invoke(cli.cli, ["-S", "0.0.500.0", "-P", "80", "192.0.2.15"])
    assert result.exit_code == 2
    assert "Invalid server IP provided" in result.output


def test_cli_server_address_is_any():
    server_mock = Mock()
    with patch("noc.traffic.dns.safedns.dnsl3r.dnsl3r.cli.server.run_sanic_server", new=server_mock):
        result = CliRunner().invoke(cli.cli, ["-S", "any", "-P", "80", "192.0.2.15"])
    server_mock.assert_called_once()
    assert result.exit_code == 0


def test_cli_query_timeout_bigger_than_query_period():
    result = CliRunner().invoke(
        cli.cli, ["--query-period", "5", "--query-timeout", "10", "-S", "any", "-P", "80", "192.0.2.15"]
    )
    assert result.exit_code == 2
    assert "Query timeout must be between" in result.output


def test_cli_query_period_is_too_long():
    result = CliRunner().invoke(
        cli.cli,
        ["--query-period", str(cli.MAX_PERIOD + 1), "--query-timeout", "10", "-S", "any", "-P", "80", "192.0.2.15"],
    )
    assert result.exit_code == 2
    assert "Invalid value" in result.output


def test_cli_self_dn_supported():
    server_mock = Mock()
    with patch("noc.traffic.dns.safedns.dnsl3r.dnsl3r.cli.server.run_sanic_server", new=server_mock):
        result = CliRunner().invoke(cli.cli, ["--query-dn", "$self", "-S", "any", "-P", "80", "192.0.2.15"])
    server_mock.assert_called_once()
    assert result.exit_code == 0
