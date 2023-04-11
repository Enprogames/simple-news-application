"""
Helper script for initializing and destroying database content.

@author: Ethan Posner
@date: 2023-04-10
"""

import os
from pathlib import Path
import argparse

# Third party imports
from dotenv import load_dotenv
import oracledb


def execute_script(script_name: str, cursor: 'Cursor') -> str:
    content = ""
    with open(Path(__file__).parent / script_name, 'r') as f:
        for line in f.readlines():
            if not line.startswith('--'):  # skip lines starting with '--'
                if '--' in line:  # if line contains '--', remove everything after it
                    line = line[:line.index('--')]
                content += "\n" + line

    for statement in content.split(';'):
        statement = statement.strip()
        if statement and not statement.isspace():
            print(statement)
            try:
                cursor.execute(statement)
                print('Success!')
            except oracledb.DatabaseError as e:
                print('*' * 80)
                print('*' * 80)
                print(f'Error: {e}')
                print('Skipping to next statement...')
                print('*' * 80)
                print('*' * 80)


parser = argparse.ArgumentParser(description='Run create_data.sql or drop_tables.sql script.')
parser.add_argument('--create', help='Run create_data.sql script.', action='store_true')
parser.add_argument('--drop', help='Run drop_tables.sql script.', action='store_true')
args = parser.parse_args()


load_dotenv()  # load environment from .env file
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
oracledb.init_oracle_client()
with oracledb.connect(user=os.getenv('DB_USER'),
                      password=os.getenv('DB_PASS'),
                      port=os.getenv('DB_PORT'),
                      host=os.getenv('DB_HOST'),
                      service_name='XE') as db_conn:
    
    if args.create:
        with db_conn.cursor() as cursor:
            execute_script('create_data.sql', cursor)
        db_conn.commit()
    elif args.drop:
        with db_conn.cursor() as cursor:
            execute_script('drop_tables.sql', cursor)
        db_conn.commit()
    else:
        raise ValueError("Invalid arguments. Must specify --create or --drop")
