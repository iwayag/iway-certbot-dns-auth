NAME=iway-certbot-dns-auth
VERSION=$(shell git describe --abbrev=0)
PACKAGE=$(NAME)-$(VERSION).tar.gz
MODULE=iway_certbot_dns_auth

.PHONY: version test clean distclean

.venv:
	mkdir .venv
	poetry init

version:
	poetry version $(VERSION)

dist/$(PACKAGE): version
	poetry build

build: dist/$(PACKAGE)

publish: dist/$(PACKAGE)
	poetry publish --username=${PYPI_USERNAME} --password=${PYPI_PASSWORD}

test:
	pytest 

clean:
	rm -rf dist

distclean: clean
	rm -rf *.egg-info/