.PHONY: venv
venv:
	if [ ! -d "venv" ]; then python3 -m venv venv; fi
	venv/bin/pip3 install -r requirements.txt

venv-pylint: venv
	venv/bin/pip3 install pylint pylint-exit anybadge
