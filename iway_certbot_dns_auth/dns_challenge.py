"""
DNS challenge authentication hook for certbot.

certbot will provide the following environment variables:

* CERTBOT_DOMAIN
* CERTBOT_VALIDATION
* CERTBOT_TOKEN
* CERTBOT_CERT_PATH
* CERTBOT_KEY_PATH
* CERTBOT_SNI_DOMAIN
* CERTBOT_AUTH_OUTPUT
"""

import os
import sys
import logging

from .utils import Config, is_wildcard, clean_domain_name, string_to_idna, idna_to_string
from .api import PortalApi


class DnsChallengeHookError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        logging.getLogger(__package__).exception(self)
        sys.exit(1)


class DnsChallengeHook:
    def __init__(self) -> None:
        try:
            self.domain = os.environ['CERTBOT_DOMAIN']
            self.validation = os.environ['CERTBOT_VALIDATION']
            self.auth_output = os.environ.get('CERTBOT_AUTH_OUTPUT')
        except Exception as exc:
            raise DnsChallengeHookError(
                'could not read environment: %s' % exc) from exc

        try:
            self.config: Config = Config()
        except Exception as exc:
            raise DnsChallengeHookError(
                'could not read config: %s' % exc) from exc

        try:
            self.api = PortalApi(
                self.config['account']['username'],
                self.config['account']['password'])
        except Exception as exc:
            raise DnsChallengeHookError(
                'could not connect API: %s' % exc) from exc

        self.clean_domain = idna_to_string(clean_domain_name(self.domain))
        self.idna_domain = string_to_idna(self.clean_domain)
        self.auth_record = "_acme-challenge.%s" % self.clean_domain

    def auth(self) -> None:
        """Authentication hook."""

        try:
            zone: dict = self.api.get_zone(self.idna_domain)
            rrsets = zone['rrsets']

            # for none wildcard domains check if domain record exists
            if not is_wildcard(self.domain):
                domain_record = self.clean_domain
                for rrset in rrsets:
                    if (rrset['type'] in ('A', 'AAA', 'CNAME')
                            and rrset['name'] == domain_record):
                        break
                else:
                    raise DnsChallengeHookError(
                        "domain record '%s' doesn't exists in '%s'" % (
                            domain_record, self.clean_domain))

            for rrset in rrsets:
                if (rrset['type'] == 'TXT'
                        and rrset['name'] == self.auth_record):
                    logging.getLogger(__package__).debug(
                        "update existing auth record '%s' in '%s'",
                        self.auth_record, self.clean_domain)
                    rrset.update({
                        'changetype': 'REPLACE',
                        'ttl': 300,
                        'records': [{
                            'content': '"%s"' % self.validation,
                            'disabled': False,
                        }],
                    })
                    break
            else:
                logging.getLogger(__package__).debug(
                    "add auth record '%s' to '%s'",
                    self.auth_record, self.clean_domain)

                rrset = {
                    'changetype': 'REPLACE',
                    'name': self.auth_record + ".",
                    'type': 'TXT',
                    'ttl': 300,
                    'records': [{
                        'content': '"%s"' % self.validation,
                        'disabled': False,
                    }],
                }

            zone['rrsets'] = [rrset]

            self.api.set_zone_records(self.idna_domain, zone)

        except DnsChallengeHookError as exc:
            raise
        except Exception as exc:
            raise DnsChallengeHookError(exc) from exc

    def cleanup(self):
        """Cleanup hook."""

        try:
            zone = self.api.get_zone(self.idna_domain)
            rrsets = zone['rrsets']

            for rrset in rrsets:
                if (rrset['type'] == 'TXT'
                        and rrset['name'] == self.auth_record):
                    logging.getLogger(__package__).debug(
                        "delete auth record '%s' from '%s'",
                        self.auth_record, self.clean_domain)

                    rrset.update({'changetype': 'DELETE'})
                    break
            else:
                raise DnsChallengeHookError(
                    "record %s does not exists in '%s'".format(
                        self.auth_record, self.clean_domain))

            zone['rrsets'] = [rrset]

            self.api.set_zone_records(self.idna_domain, zone)

        except DnsChallengeHookError as exc:
            raise
        except Exception as exc:
            raise DnsChallengeHookError(exc) from exc
