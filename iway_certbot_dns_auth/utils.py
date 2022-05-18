"""Utils module."""

import os
import sys
import yaml
import logging
from logging import config


def is_wildcard(domain_name: str) -> bool:
    return domain_name.startswith('*.')


def clean_domain_name(domain_name: str) -> str:
    if is_wildcard(domain_name):
        return domain_name[2:]
    else:
        return domain_name


def string_to_idna(s):
    if isinstance(s, str):
        return s.encode("idna").decode()
    raise TypeError('string expected')


def idna_to_string(s):
    if isinstance(s, str):
        try:
            return s.encode().decode("idna")
        except UnicodeDecodeError as exc:
            # assume is already decoded
            return s
    raise TypeError('string expected')


class Config(dict):
    """Config class."""

    env_config: str = 'IWAY_CERTBOT_DNS_AUTH_CFG'
    default_config: str = '/etc/iway-certbot-dns-auth.yml'

    def __init__(self, cfg_file: str = None) -> None:
        self.cfg_file = (
            cfg_file
            or os.environ.get(self.env_config)
            or self.default_config)

        with open(self.cfg_file) as cfg:
            logging.getLogger(__package__).debug(
                'read config file %s: %s', self.cfg_file)

            for key, value in yaml.load(
                    cfg, Loader=yaml.FullLoader).items():
                self[key] = value

        # setup logging
        syslog = True
        address = ('localhost', 514)
        facility = 'local0'
        level = 'INFO'
        format = '%(asctime)s %(levelname)s %(name)s: %(message)s'

        if sys.platform == "darwin":
            address = '/var/run/syslog'
            facility = 'local1'
        elif sys.platform == 'linux':
            address = '/dev/log'
            facility = 'local0'

        if 'logging' in self:
            log_cfg = self['logging']
            address = log_cfg.get('address') or address
            facility = log_cfg.get('facility') or facility
            format = log_cfg.get('format') or format
            syslog = syslog if log_cfg.get(
                'syslog') is None else log_cfg.get('syslog')
            level = log_cfg.get('level') or level

        log_dict = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose': {
                    'format': format
                },
            },
            'handlers': {
                'stderr': {
                    'class': 'logging.StreamHandler',
                    'stream': sys.stderr,
                    'formatter': 'verbose',
                    'level': 'ERROR',
                },
                'syslog': {
                    'class': 'logging.handlers.SysLogHandler',
                    'address': address,
                    'facility': facility,
                    'formatter': 'verbose',
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose'
                },
            },
            'loggers': {
                '': {
                    'handlers': ['stderr'],
                    'level': level,
                    'propagate': False
                },
                'iway_certbot_dns_auth': {
                    'handlers': ['console'],
                    'level': level,
                    'propagate': False
                },
            }
        }

        if syslog:
            log_dict['loggers']['']['handlers'].append('syslog')
            log_dict['loggers']['iway_certbot_dns_auth']['handlers'].append(
                'syslog')

        config.dictConfig(log_dict)
