# vim: noexpandtab, tabstop=4
#
# Install the scrips, configs and python modules
#

PACKAGE= $(shell basename ${PWD})
VERSION= $(shell awk -F\' '/^VERSION/ {print $$2}' setup.py)
SYSTEM= $(shell uname -s)

ifeq ($(SYSTEM),Darwin)
PREFIX_INSTALL_FLAGS='--no-user-cfg'
else
PREFIX_INSTALL_FLAGS=
endif

all: build

clean:
	@rm -rf build
	@rm -rf dist
	@find . -name '*.pyc' -o -name '*.egg-info'|xargs rm -rf

build:
	python setup.py build

ifdef PREFIX
install_modules: build
	python setup.py $(PREFIX_INSTALL_FLAGS) install --prefix=${PREFIX}
install: install_modules 
	install -m 0755 -d $(PREFIX)/bin
	for f in bin/*; do echo " $(PREFIX)/$$f";install -m 755 $$f $(PREFIX)/bin/;done;
else
install_modules: build 
	python setup.py install
install: install_modules 
endif

package: clean
	mkdir -p ../../Releases/$(PACKAGE)
	git log --pretty=format:'%ai %an%n%n%B' > CHANGELOG.txt
	rsync -a . --exclude='*.swp' --exclude=.DS_Store --exclude=.idea --exclude=.git --exclude=.gitignore ./ $(PACKAGE)-$(VERSION)/
	rm CHANGELOG.txt
	tar -zcf ../../Releases/$(PACKAGE)/$(PACKAGE)-$(VERSION).tar.gz --exclude=.git --exclude=.gitignore --exclude=*.swp --exclude=*.pyc $(PACKAGE)-$(VERSION) 
	rm -rf $(PACKAGE)-$(VERSION)

register:
	python setup.py register

