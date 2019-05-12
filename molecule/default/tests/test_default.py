"""Module containing the tests for the default scenario."""

import datetime
import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


@pytest.mark.parametrize("pkg", ["aptitude"])
def test_debian_packages(host, pkg):
    """Test that appropriate packages were installed on Debian."""
    ansible_vars = host.ansible.get_variables()
    if ansible_vars["inventory_hostname"] in ansible_vars['groups']['debian']:
        assert host.package(pkg).is_installed


def test_debian_upgraded(host):
    """Test that Debian instances were upgraded."""
    ansible_vars = host.ansible.get_variables()
    if ansible_vars["inventory_hostname"] in ansible_vars['groups']['debian']:
        assert (datetime.datetime.now() - host.file("/var/cache/apt").mtime).total_seconds() <= 24 * 60 * 60


def test_redhat_upgraded(host):
    """Test that RedHat instances were upgraded."""
    ansible_vars = host.ansible.get_variables()
    if ansible_vars["inventory_hostname"] in ansible_vars['groups']['amazon']:
        last_installation = datetime.datetime.strptime(host.run("rpm -qa --queryformat '%{installtime} %{installtime:date}\n' | sort --numeric-sort | tail --lines=1 | cut --delimiter=' ' --fields=2-").stdout, "%a %b %d %H:%M:%S %Y")
        assert (datetime.datetime.now() - last_installation).total_seconds() <= 24 * 60 * 60
