
all: build

clean:
	@rm -rf build
	@rm -rf dist
	@find . -name '*.egg-info' -print0|xargs -0 rm -rf
	@find . -name '*.pyc' -print0|xargs -0 rm -rf

build:
	python setup.py build

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

upload: clean
	python setup.py sdist bdist_wheel
	twine upload dist/*
