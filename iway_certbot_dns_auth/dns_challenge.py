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
import time # Needed for DNS propagation delay

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
            # Determine the correct zone name and its IDNA version
            # The API expects the base zone (e.g., 'my-domain.com'), not the full subdomain.
            if 'dns-zone' in self.config:
                self.zone_domain = self.config['dns-zone']
            else:
                domain_parts = self.domain.split('.')
                if len(domain_parts) >= 2:
                    self.zone_domain = '.'.join(domain_parts[-2:])
                else:
                    self.zone_domain = self.domain
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

        # The IDNA-encoded zone domain (used for API calls)
        self.idna_zone_domain = string_to_idna(self.zone_domain)

        # The clean_domain and auth_record use the FULL domain, which is correct for the record name
        self.clean_domain = idna_to_string(clean_domain_name(self.domain))
        # Note: self.idna_domain is no longer used for API calls but is kept if other logic needs it
        # self.idna_domain = string_to_idna(self.clean_domain)
        self.auth_record = "_acme-challenge.%s" % self.clean_domain

    def auth(self) -> None:
        """Authentication hook."""

        try:
            # Use the calculated base zone domain for get_zone()
            zone: dict = self.api.get_zone(self.idna_zone_domain)
            rrsets = zone['rrsets']
            auth_rrset = None 

            # Look for an existing TXT record for the ACME challenge
            for rrset in rrsets:
                # The name comparison needs to be robust (comparing against name + ".")
                if (rrset['type'] == 'TXT'
                        and rrset['name'] == self.auth_record + "."):
                    
                    logging.getLogger(__package__).debug(
                        "update existing auth record '%s' in '%s'",
                        self.auth_record, self.zone_domain)
                    
                    rrset.update({
                        'changetype': 'REPLACE',
                        'ttl': 300,
                        'records': [{
                            'content': '"%s"' % self.validation,
                            'disabled': False,
                        }],
                    })
                    auth_rrset = rrset
                    break
            else:
                logging.getLogger(__package__).debug(
                    "add auth record '%s' to '%s'",
                    self.auth_record, self.zone_domain)

                # Record not found, create a new one
                auth_rrset = {
                    'changetype': 'REPLACE',
                    'name': self.auth_record + ".",
                    'type': 'TXT',
                    'ttl': 300,
                    'records': [{
                        'content': '"%s"' % self.validation,
                        'disabled': False,
                    }],
                }

            # Ensure only the single, modified/new rrset is sent to the API
            if not auth_rrset:
                 raise DnsChallengeHookError("Failed to create or find auth record definition.")

            zone['rrsets'] = [auth_rrset] # Send ONLY the change

            # Use the calculated base zone domain for set_zone_records()
            self.api.set_zone_records(self.idna_zone_domain, zone)
            
            # Add a short delay to allow DNS propagation before validation starts
            logging.getLogger(__package__).debug("Waiting 10 seconds for DNS propagation...")
            time.sleep(3)

        except DnsChallengeHookError as exc:
            raise
        except Exception as exc:
            raise DnsChallengeHookError(exc) from exc

    def cleanup(self):
        """Cleanup hook."""

        try:
            # Use the calculated base zone domain for get_zone()
            zone = self.api.get_zone(self.idna_zone_domain)
            rrsets = zone['rrsets']
            auth_rrset = None
            
            # Check against both FQDN (with dot) and non-FQDN (without dot) 
            # to be robust against API inconsistencies
            name_with_dot = self.auth_record + "."
            name_without_dot = self.auth_record

            for rrset in rrsets:
                if rrset['type'] == 'TXT' and (
                        rrset['name'] == name_with_dot or 
                        rrset['name'] == name_without_dot):
                    
                    logging.getLogger(__package__).debug(
                        "delete auth record '%s' from '%s'",
                        self.auth_record, self.zone_domain)

                    rrset.update({'changetype': 'DELETE'})
                    auth_rrset = rrset
                    break
            else:
                # Use the calculated zone domain and correct formatting for the error message
                raise DnsChallengeHookError(
                    "record {} does not exists in '{}'".format(
                        self.auth_record, self.zone_domain))

            # Ensure only the change is sent
            if not auth_rrset:
                return 

            zone['rrsets'] = [auth_rrset] # Send ONLY the deletion

            # Use the calculated base zone domain for set_zone_records()
            self.api.set_zone_records(self.idna_zone_domain, zone)

        except DnsChallengeHookError as exc:
            raise
        except Exception as exc:
            raise DnsChallengeHookError(exc) from exc

