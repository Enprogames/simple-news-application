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
	@echo "    Setup the virtual environment."
	@echo "make run"
	@echo "    Run the program."

setup: requirements.txt
	python3 -m venv $(venvDIR) --prompt $(projectName)
	$(venvDIR)/bin/pip install -r requirements.txt

run:
	$(venvDIR)/bin/python3 $(codeDIR)/main.py

clean:
	rm -rf $(venvDIR)

.PHONY: help setup run clean
