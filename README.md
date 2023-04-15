# CSCI 370 - Final Project - News Database

## Description
Uses oracle database and Python. See `docs/posnerem_CSCI_370_Project_Report.md` for more details.

## Setup
### Using Makefile
1. `make setup` to create virtual environment and install dependencies
2. Fill in values in .env file
3. Run `make initdb` after filling in values in .env file to setup database
4. Run `make run` to run the program

### Manual Setup
1. Copy .env.example to .env and fill in the values: `cp .env.example .env`
2. Create virtual environment: `python3 -m venv venv --prompt csci370-news`
3. Activate virtual environment: `source venv/bin/activate`
4. Initialize database with `python3 src/db_util.py --create` or by running the `create_data.sql` file in SQLPlus
5. Install dependencies: `pip install -r requirements.txt`
    - Deactivate virtual environment: `deactivate`

## Usage

1. Run the program: `python main.py` or `make run`
2. Follow the prompts

## Cleaning Up
- Run `make clean` to remove virtual environment and database files
or
- `python3 src/db_util.py --drop`

## Testing
1. Run `make test` to run tests
