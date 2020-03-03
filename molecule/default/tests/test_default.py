"""Module containing the tests for the default scenario."""

# Standard Python Libraries
import datetime
import os

# Third-Party Libraries
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


@pytest.mark.parametrize("pkg", ["aptitude"])
def test_debian_packages(host, pkg):
    """Test that appropriate packages were installed on Debian."""
    ansible_vars = host.ansible.get_variables()
    if ansible_vars["inventory_hostname"] in ansible_vars["groups"]["debian"]:
        assert host.package(pkg).is_installed


def test_debian_updated(host):
    """Test that Debian instances were updated."""
    ansible_vars = host.ansible.get_variables()
    if ansible_vars["inventory_hostname"] in ansible_vars["groups"]["debian"]:
        print(host.file("/var/lib/apt/lists").mtime)
        # Make sure that the instance was updated in the last 10
        # minutes
        assert (
            datetime.datetime.now() - host.file("/var/lib/apt/lists").mtime
        ).total_seconds() <= 10 * 60


# This test can fail if there were no updates to install.
@pytest.mark.xfail
def test_redhat_updated_time(host):
    """Test that RedHat instances were updated."""
    ansible_vars = host.ansible.get_variables()
    if ansible_vars["inventory_hostname"] in ansible_vars["groups"]["redhat"]:
        last_update = datetime.datetime.strptime(
            host.run(
                "yum --quiet history list | cut --delimiter='|' --fields=3-4 | grep -F U | cut --delimiter='|' --fields=1 | head --lines=1"
            ).stdout.strip(),
            "%Y-%m-%d %H:%M",
        )
        # Make sure that the instance was updated in the last 10
        # minutes
        assert (datetime.datetime.now() - last_update).total_seconds() <= 10 * 60


def test_redhat_updated_command_output(host):
    """Test that RedHat instances were updated."""
    ansible_vars = host.ansible.get_variables()
    if ansible_vars["inventory_hostname"] in ansible_vars["groups"]["redhat"]:
        yum_output = host.run("yum update")
        # If the update succeeded or there was nothing to update
        assert (
            "No packages marked for update" in yum_output.stdout
            or "Nothing to do" in yum_output.stdout
        )
