#!/bin/python3.11
"""

capture stuff over time to calc an average

"""
import json
import subprocess
import sys
from datetime import datetime

import psutil
from knxrcore.logger.logger import Logger, LogLevel

from monitoring.clientSideMonitoring.utils import is_linux, check_for_new_logins, get_limits, limit_check

__version__ = 'v1.23.4'
update = __version__

banner = f"""    __ __ _______   _________  __ ___    ____ 
   / //_// ____/ | / / ____/ |/ //   |  / __ \\
  / ,<  / __/ /  |/ / __/  |   // /| | / /_/ /
 / /| |/ /___/ /|  / /___ /   |/ ___ |/ _, _/ 
/_/ |_/_____/_/ |_/_____//_/|_/_/  |_/_/ |_|
          Logging System {__version__}
          latest server version {update}
"""


def main() -> int:
    last_login: bytes = b''

    # start up sequence
    print('-'*50)
    print(banner)
    print('-'*50)
    print('Logging will start now...')

    while True:
        config: dict

        with open('./config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        logger = Logger(LogLevel.INFO, log_file=f'{datetime.now().strftime("%Y-%d-%m")}.log', api_url=config['api'])
        ssh_users = ''
        for j in config['ssh_names']:
            ssh_users += f'{j}|'

        # limits
        cpu_limits, drive_limits, ram_limits = get_limits(config)

        # Timer is for flattening the Cpu graph output, prevent cpu performance spikes to send emails! :)
        # the higher, the better, but 5 is a good value.

        if config['timer'] <= 0:
            raise ValueError('Timer can\'t be 0 or below')

        cpu_usage = psutil.cpu_percent(interval=config['timer'])
        mem = psutil.virtual_memory()

        stats = {
            'cpu': {
                'usage': cpu_usage
            },
            'ram': {
                'usage': mem.percent,
                'available': float(f'{mem.available / 1000000000:.3f}')
            },
            'disc': {}
        }

        for i, (v, *_) in enumerate(psutil.disk_partitions()):
            temp = psutil.disk_usage(v)

            if is_linux():
                temp = psutil.disk_usage('/')

            stats['disc'].update({
                i: {
                    'usage': temp.percent,
                    'free': float(f'{temp.free / 1000000000:.3f}'),
                    'used': float(f'{temp.used / 1000000000:.3f}')
                }
            })

            if is_linux():
                break

        cpu_usage = stats['cpu'].get('usage', 0)
        ram_usage = stats['ram'].get('usage', 0)

        limit_check(cpu_limits, cpu_usage, logger, 'cpu')
        limit_check(ram_limits, ram_usage, logger, 'ram')

        for _, item in stats['disc'].items():
            drive_usage = item['usage']

            limit_check(drive_limits, drive_usage, logger, 'drive')

        # New logins
        if is_linux():
            sub_res = subprocess.run(f'last | grep -E "{ssh_users[0:-1]}" | head -n 1'.split(),
                                     capture_output=True, check=True)
            last_login, *_ = check_for_new_logins(last_login, logger, sub_res)

    return 0


if __name__ == '__main__':
    sys.exit(main())
