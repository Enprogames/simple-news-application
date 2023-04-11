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



setup: requirements.txt create_data.sql
	sqlplus posnerem@XE < create_data.sql
	cp .env.example .env
	python3 -m venv $(venvDIR) --prompt $(projectName)
	$(venvDIR)/bin/pip install -r requirements.txt

run:
	$(venvDIR)/bin/python3 $(codeDIR)/main.py

clean:
	sqlplus posnerem@XE < drop_tables.sql
	rm -rf $(venvDIR)
	rm -rf __pycache__
	rm -rf $(codeDIR)/__pycache__
	rm .env

.PHONY: help setup run clean
