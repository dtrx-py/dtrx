# A small bit of automation for various steps in building + releasing dtrx

DTRX_TAGNAME=$(shell python -c 'from dtrx import dtrx; print(dtrx.VERSION)')

# require make 4.3+ for grouped targets
MINIMUM_MAKE_VERSION = 4.3
MAKE_TEST_VERSION = $(shell printf "%s\n%s" $(MAKE_VERSION) $(MINIMUM_MAKE_VERSION) | sort --version-sort)
ifneq ($(MINIMUM_MAKE_VERSION),$(firstword $(MAKE_TEST_VERSION)))
$(error Make version is too low. Please upgrade to $(MINIMUM_MAKE_VERSION) or higher.)
endif

BUILD_ARTIFACTS= \
    dist/dtrx-$(DTRX_TAGNAME).py \
    dist/dtrx-$(DTRX_TAGNAME).pyz \
    dist/dtrx-$(DTRX_TAGNAME)-py2.py3-none-any.whl \
    dist/dtrx-$(DTRX_TAGNAME).tar.gz \

.PHONY: build
build: $(BUILD_ARTIFACTS)

# copy the standalone script too into ./dist/
dist/dtrx-$(DTRX_TAGNAME).py: dtrx/dtrx.py
	mkdir -p $(dir $@)
	cp $^ $@

# generate a zipapp
dist/dtrx-$(DTRX_TAGNAME).pyz: dtrx/dtrx.py
	mkdir -p $(dir $@)
	python -m zipapp dtrx --compress --main "dtrx:main" --python "/usr/bin/env python" --output $@

# build the wheel and source dist
dist/dtrx-$(DTRX_TAGNAME)-py2.py3-none-any.whl dist/dtrx-$(DTRX_TAGNAME).tar.gz &: dtrx/dtrx.py
	uv build --no-build-logs

.PHONY: publish-release
publish-release: $(BUILD_ARTIFACTS)
# first confirm that we're on a tag
	@git describe --exact-match > /dev/null || (echo ERROR: not on a tag; false)
# if PYPI_TOKEN is not set, fail
	@test -n "$$PYPI_TOKEN" || (echo "ERROR: PYPI_TOKEN environment variable is not set"; false)
# prompt before firing off the release
	@echo -n "About to publish to GitHub and PyPi, are you sure? [y/N] " && read ans && [ $${ans:-'N'} = 'y' ]
	gh release create --generate-notes $(DTRX_TAGNAME)
	gh release upload $(DTRX_TAGNAME) dist/*
	uv publish --token="${PYPI_TOKEN}"dist/dtrx-$(DTRX_TAGNAME).tar.gz dist/dtrx-$(DTRX_TAGNAME)-py2.py3-none-any.whl
