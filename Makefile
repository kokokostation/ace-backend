install-dev-requirements:
	pip install -r dev-requirements.txt

mypy:
	mypy

black:
	black .

build:
	rm -rf /tmp/ace-backend
	mkdir /tmp/ace-backend
	python -m build -o /tmp/ace-backend/build

upload:
	twine upload /tmp/ace-backend/build/*.tar.gz
