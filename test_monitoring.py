import json
import subprocess

from knxrcore.logger import Logger

import monitoring.clientSideMonitoring.utils as u


def test_is_linux():
    assert u.is_linux(), 'Should be linux'


def test_check_for_new_login():
    res = subprocess.run('last | grep "julian" | head -n 1'.split(), check=True, capture_output=True)
    _, status_code = u.check_for_new_logins(b'', Logger(5), res)

    assert not status_code, 'Should be 0'


def test_limits():
    with open('monitoring/clientSideMonitoring/config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    cpu_limit, *_ = u.get_limits(config)
    logger = Logger(5)

    limit_check_code, status_code = u.limit_check(cpu_limit, 95, logger, 'cpu')

    assert not limit_check_code and status_code == 404, 'Should be 1'


if __name__ == '__main__':
    test_check_for_new_login()
