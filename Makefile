export PATH := ./venv/bin:$(PATH)

init: sync

python:
	asdf install

venv: python
	python -m venv venv

pip-tools: venv
	pip install --quiet --upgrade pip pip-tools

requirements/base.txt: requirements/base.in pip-tools
	pip-compile \
		--quiet \
		--output-file $@ \
		$<

requirements/dev.txt: requirements/dev.in pip-tools
	pip-compile \
		--quiet \
		--output-file $@ \
		$<

sync: requirements/base.txt requirements/dev.txt
	pip-sync $^

clean:
	rm -rf photos