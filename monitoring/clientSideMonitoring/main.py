#!/bin/python3.11
"""

capture stuff over time to calc an average

"""
import json
import sys
import platform

import psutil

from knxrcore.logger.logger import Logger, LogLevel


def main() -> int:
    while True:
        c: dict

        with open('./config.json', 'r') as f:
            c = json.load(f)

        logger = Logger(LogLevel.INFO, log_file='monitoring.log', api_url=c['api'])

        # limits
        cpu_limits = (c['hard'].get('cpu', 95), c['hard'].get('cpu', 80))
        ram_limits = (c['hard'].get('ram', 90), c['hard'].get('ram', 80))
        drive = (c['hard'].get('drive', 90), c['hard'].get('drive', 70))

        cpu_usage = psutil.cpu_percent(interval=1)
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

            if 'linux' in platform.platform().lower():
                temp = psutil.disk_usage('/')

            stats['disc'].update({
                i: {
                    'usage': temp.percent,
                    'free': float(f'{temp.free / 1000000000:.3f}'),
                    'used': float(f'{temp.used / 1000000000:.3f}')
                }
            })

            if 'linux' in platform.platform().lower():
                break

        print(stats)

        if stats['cpu'].get('usage') >= cpu_limits[1]:
            if stats['cpu'].get('usage') >= cpu_limits[0]:
                logger.error('Cpu has exceeded its hard limits').get_api('burn/1337/cpu',
                                                                         value=stats['cpu'].get('usage'), limit='hard')
                continue

            logger.warning('Cpu has exceeded its soft limits').get_api('burn/1337/cpu',
                                                                       value=stats['cpu'].get('usage'), limit='soft')
            continue

    return 0


if __name__ == '__main__':
    sys.exit(main())
