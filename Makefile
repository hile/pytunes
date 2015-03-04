# vim: noexpandtab, tabstop=4
#
# Install the scrips, configs and python modules
#

PACKAGE= $(shell basename ${PWD})
VERSION= $(shell awk -F\' '/^VERSION/ {print $$2}' setup.py)

all: build

clean:
	@rm -rf build
	@rm -rf dist
	@find . -name '*.egg-info' -print0|xargs -0 rm -rf
	@find . -name '*.pyc' -print0|xargs -0 rm -rf

build:
	python setup.py build

.PHONY: test
test:
	python -m unittest test

ifdef PREFIX
install_modules: build
	python setup.py --no-user-cfg install --prefix=${PREFIX}
install: install_modules
	install -m 0755 -d $(PREFIX)/bin
	for f in bin/*; do echo " $(PREFIX)/$$f";install -m 755 $$f $(PREFIX)/bin/;done;
else
install_modules: build
	python setup.py install
install: install_modules
endif

package: clean
	mkdir -p ../releases/$(PACKAGE)
	git log --pretty=format:'%ai %an%n%n%B' > CHANGELOG.txt
	rsync -a . --exclude='*.swp' --exclude=.git --exclude=.gitignore ./ $(PACKAGE)-$(VERSION)/
	rm CHANGELOG.txt
	tar -zcf ../releases/$(PACKAGE)/$(PACKAGE)-$(VERSION).tar.gz --exclude=.git --exclude=.gitignore --exclude=*.swp --exclude=*.pyc $(PACKAGE)-$(VERSION)
	rm -rf $(PACKAGE)-$(VERSION)

register:
	python setup.py register sdist upload

