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

        with open('./config.json', 'r', encoding='utf-8') as f:
            c = json.load(f)

        logger = Logger(LogLevel.INFO, log_file='monitoring.log', api_url=c['api'])

        # limits
        cpu_limits = (c['hard'].get('cpu', 95), c['hard'].get('cpu', 80))
        ram_limits = (c['hard'].get('ram', 90), c['hard'].get('ram', 80))
        drive_limits = (c['hard'].get('drive', 90), c['hard'].get('drive', 70))

        # Timer is for flattening the Cpu graph output, prevent cpu performance spikes to send emails! :)
        # the higher, the better, but 5 is a good value.

        if c['timer'] <= 0:
            raise ValueError('Timer can\'t be 0 or below')

        cpu_usage = psutil.cpu_percent(interval=c['timer'])
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

        cpu_usage = stats['cpu'].get('usage', 0)
        ram_usage = stats['ram'].get('usage', 0)

        if cpu_usage >= cpu_limits[1]:
            if cpu_usage >= cpu_limits[0]:
                logger.error('Cpu has exceeded its hard limits').get_api('burn/1337/cpu',
                                                                         value=cpu_usage, hard=True)
                continue

            logger.warning('Cpu has exceeded its soft limits').get_api('burn/1337/cpu',
                                                                       value=cpu_usage)
            continue

        if ram_usage >= ram_limits[1]:
            if ram_usage >= ram_limits[0]:
                logger.error('Ram has exceeded its hard limits').get_api('burn/1337/ram',
                                                                         value=ram_usage, hard=True)
                continue
            logger.warning('Ram has exceeded its soft limits').get_api('burn/1337/ram',
                                                                       value=ram_usage)
            continue

        for _, item in stats['disc'].items():
            drive_usage = item['usage']

            if drive_usage >= drive_limits[1]:
                if drive_usage >= drive_limits[0]:
                    logger.error('Drive has exceeded its hard limits').get_api('burn/1337/drive',
                                                                               value=drive_usage, hard=True)
                    continue

                logger.warning('Drive has exceeded its soft limits').get_api('burn/1337/drive',
                                                                             value=ram_usage)
    return 0


if __name__ == '__main__':
    sys.exit(main())
