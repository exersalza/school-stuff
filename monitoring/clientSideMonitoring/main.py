"""

capture stuff over time to calc an average

"""
import json
import psutil

from knxrcore.logger.logger import Logger, LogLevel


def main() -> int:
    c: dict

    with open('./config.json', 'r') as f:
        c = json.load(f)

    logger = Logger(LogLevel.INFO, log_file='monitoring.log', api_url=c['api'])

    # limits
    cpu_limits = (c['hard'].get('cpu', 95), c['hard'].get('cpu', 80))
    ram_limits = (c['hard'].get('ram', 90), c['hard'].get('ram', 80))
    drive = (c['hard'].get('drive', 90), c['hard'].get('drive', 70))

    cpu_usage = psutil.cpu_percent(interval=5)
    mem = psutil.virtual_memory()
    disc = psutil.disk_usage('/')

    stats = {
        'cpu': {
            'usage': cpu_usage
        },
        'ram': {
            'usage': mem.percent,
            'available': float(f'{mem.available / 1000000000:.3f}')
        },
        'disc': {
            'usage': disc.percent,
            'left': float(f'{disc.free / 1000000000:.3f}'),
            'used': float(f'{disc.used / 1000000000:.3f}')
        }
    }
    print(stats)

    if stats['cpu'].get('usage') >= cpu_limits[1]:
        if stats['cpu'].get('usage') >= cpu_limits[0]:
            pass
    logger.error('Cpu has exceeded its hard limits').get_api('burn/1337/cpu', value=stats['cpu'].get('usage'))

    return 0


if __name__ == '__main__':
    exit(main())
