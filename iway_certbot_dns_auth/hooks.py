import sys
from iway_certbot_dns_auth import DnsChallengeHook


def certbot_auth_hook():
    DnsChallengeHook().auth()
    sys.exit(0)


def certbot_cleanup_hook():
    DnsChallengeHook().cleanup()
    sys.exit(0)
