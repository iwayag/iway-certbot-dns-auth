# iway-certbot-dns-auth

Certbot hook for DNS challenge using iWay Portal API.

## Dependencies

To use this module the certbot (https://certbot.eff.org/) is required:

    apt install certbot

## Install

    pip install iway_certbot_dns_auth

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
      username: 12345
      password: 'changeme'
    logging:
      syslog: true

## Usage

Create a new cert for your domain `my-domain.com` with:

    PATH=$PATH:/usr/local/lib/python3.8/dist-packages/scripts \
    certbot \
      certonly \
      --email me@gmail.com \
      --no-eff-email \
      --agree-tos \
      --preferred-challenges 'dns' \
      --manual \
      --manual-auth-hook iway-certbot-auth-hook \
      --manual-cleanup-hook iway-certbot-cleanup-hook \
      --manual-public-ip-logging-ok \
      --domain my-domain.com

Renew cert with:

    PATH=$PATH:/usr/local/lib/python3.8/dist-packages/scripts \
    certbot \
      renew \
      --force-renewal

_Note:_ `PATH` depends from your local Python version. Checkout `python -V`.
