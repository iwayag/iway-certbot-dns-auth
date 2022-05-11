NAME=iway-certbot-dns-auth
VERSION=$(shell git describe --abbrev=0)
PACKAGE=$(NAME)-$(VERSION).tar.gz

.PHONY: version test clean distclean VERSION.txt

.venv:
	mkdir .venv
	poetry init

version:
	poetry version $(VERSION)

VERSION.txt: version
	echo "$(VERSION)" > VERSION.txt

README.txt: README.md
	# apt-get install pandoc
	pandoc --from=markdown --to=plain README.md > README.txt

dist/$(PACKAGE): VERSION.txt README.txt
	# poetry build
	python setup.py sdist

build: dist/$(PACKAGE)

publish: dist/$(PACKAGE)
	poetry publish --username=${PYPI_USERNAME} --password=${PYPI_PASSWORD}

test:
	pytest 

clean:
	rm -rf dist

distclean: clean
	rm -rf *.egg-info/