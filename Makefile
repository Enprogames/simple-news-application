# Makefile for CSCI 370 Final Project
# @author: Ethan Posner
# @Date: 2023/04/10

venvDIR = venv
projectName = CSCI370FinalProject
codeDIR = src


help:
	@echo "$(projectName) Makefile usage:"
	@echo "make help"
	@echo "    Display this help message."
	@echo "make setup"
	@echo "    Setup database, create environment file, and create Python virtual environment."
	@echo "make run"
	@echo "    Run the program."
	@echo "make clean"
	@echo "    Remove the virtual environment and other junk."



setup: requirements.txt
	cp .env.example .env
	python3 -m venv $(venvDIR) --prompt $(projectName)
	$(venvDIR)/bin/pip install -r requirements.txt

# This must be ran after the .env file is given the database credentials
initdb: create_data.sql
	$(venvDIR)/bin/python3 db_util.py --create

dropdb: drop_tables.sql
	$(venvDIR)/bin/python3 db_util.py --drop

run:
	$(venvDIR)/bin/python3 $(codeDIR)/main.py

# run tests using pytest unit testing framework
test:
	$(venvDIR)/bin/pytest

clean:
	rm -rf $(venvDIR)
	rm -rf __pycache__
	rm -rf $(codeDIR)/__pycache__
	rm -f .env
	rm -rf .pytest_cache

.PHONY: help setup run clean initdb dropdb test
