# iway-certbot-dns-auth

Certbot hook for DNS challenge using iWay Portal API.

## Dependencies

To use this module the [certbot](https://certbot.eff.org/) is required of course :-)

You can [install certbot](https://certbot.eff.org/instructions?ws=other&os=debianbuster) directly by your OS (e.g. Debian)
and install `iway_certbot_dns_auth` globally with `sudo pip install iway_certbot_dns_auth`.

Or, better [install certbot in a Python virtual environment](https://certbot.eff.org/instructions?ws=other&os=pip)
together with `iway_certbot_dns_auth`.

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

    certbot \
      certonly \
      --email me@gmail.com \
      --no-eff-email \
      --agree-tos \
      --preferred-challenges dns \
      --manual \
      --manual-auth-hook /usr/local/bin/iway-certbot-auth-hook \
      --manual-cleanup-hook /usr/local/bin/iway-certbot-cleanup-hook \
      --domain my-domain.com

Renew cert with:

    certbot \
      renew \
      --force-renewal
