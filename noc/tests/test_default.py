import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import os
    import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_package_installed(host):
    p = host.package('yandex-l3mgr-balancer-agent')

    assert p.is_installed

def test_log_folder_owner(host):
    logdir = host.file("/var/log/l3mgr-balancer-agent")

    assert logdir.is_directory
    assert logdir.user == "syslog"
    assert logdir.group == "adm"

    logfile = host.file("/var/log/l3mgr-balancer-agent/agent.log")

    assert logfile.is_file
    assert logfile.user == "syslog"
    assert logfile.group == "adm"
