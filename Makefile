export PATH := ./venv/bin:$(PATH)

init: sync

python:
	asdf install

venv: python
	python -m venv venv

pip-tools: venv
	pip install --quiet --upgrade pip pip-tools

requirements/dev.txt: requirements/dev.in pip-tools
	pip-compile \
		--quiet \
		--output-file $@ \
		$<

sync: requirements/dev.txt
	pip-sync $^

clean:
	rm -rf photos