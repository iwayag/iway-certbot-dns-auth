# iway-certbot-dns-auth

Certbot hook for DNS challenge using iWay Portal API.

## Install

    pip install certbot iway_certbot_dns_auth

## Config

The hook default config file is `/etc/iway-certbot-dns-auth.yml` but can be change with the
environment variable `IWAY_CERTBOT_DNS_AUTH_CFG`.

    IWAY_CERTBOT_DNS_AUTH_CFG=/etc/my-config.yml

The file have to contain a `account` section with `username` and `password`. Further it can
contain a `logging` section with:

- `syslog` - enable Syslog (default `false`)
- `level` - log level (default `"INFO"`)
- `address` - Syslog address (default `/dev/log`)
- `facility` - Syslog facility (default `local0`)
- `format` - log format (default `"%(asctime)s %(levelname)s %(name)s: %(message)s"`)

Example `/etc/iway-certbot-dns-auth.yml`:

    account:
      username: 329901
      password: 'ceCh3Athei5Ohfa'
    logging:
      syslog: true
      level: 'DEBUG'

## Usage

    certbot \
      certonly \
      --email me@gmail.com \
      --no-eff-email \
      --quiet \
      --agree-tos \
      --preferred-challenges 'dns' \
      --preferred-chain 'ISRG Root X1' \
      --manual \
      --manual-auth-hook /path/to/auth-hook \
      --manual-cleanup-hook /path/to/cleanup-hook \
      --manual-public-ip-logging-ok \
      --domain my-domain.com,www.my-domain.com
