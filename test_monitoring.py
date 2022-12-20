import subprocess

from knxrcore.logger import Logger

import monitoring.clientSideMonitoring.utils as u


def test_is_linux():
    assert u.is_linux(), 'Should be linux'


def test_check_for_new_login():
    res = subprocess.run('last | grep "julian" | head -n 1'.split(), check=True, capture_output=True)
    _, status_code = u.check_for_new_logins(b'', Logger(5), res)

    assert not status_code, 'Should be 0'


if __name__ == '__main__':
    test_check_for_new_login()
