-include .env
export

run:
	@python -m ytparser


lint:
	@mypy ytparser
	@flake8 ytparser
