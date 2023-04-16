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


def execute_script(script_name: str, cursor: 'Cursor', output=True) -> str:
    content = ""
    with open(Path(__file__).parent.parent / script_name, 'r') as f:
        for line in f.readlines():
            if not line.startswith('--'):  # skip lines starting with '--'
                if '--' in line:  # if line contains '--', remove everything after it
                    line = line[:line.index('--')]
                content += "\n" + line

    for statement in content.split(';'):
        statement = statement.strip()
        if statement and not statement.isspace():
            if output:
                print(statement)
            try:
                cursor.execute(statement)
                if output:
                    print('Success!')
            except oracledb.DatabaseError as e:
                if output:
                    print('*' * 80)
                    print('*' * 80)
                    print(f'Error: {e}')
                    print('Skipping to next statement...')
                    print('*' * 80)
                    print('*' * 80)


def create_data(db_conn: 'Connection', output=True) -> None:
    with db_conn.cursor() as cursor:
        execute_script('create_data.txt', cursor, output=output)
    db_conn.commit()


def drop_data(db_conn: 'Connection', output=True) -> None:
    with db_conn.cursor() as cursor:
        execute_script('drop_tables.txt', cursor, output=output)
    db_conn.commit()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run create_data.txt or drop_tables.txt script.')
    parser.add_argument('--create', help='Run create_data.txt script.', action='store_true')
    parser.add_argument('--drop', help='Run drop_tables.txt script.', action='store_true')
    args = parser.parse_args()


    load_dotenv()  # load environment from .env file
    oracledb.init_oracle_client()
    with oracledb.connect(user=os.getenv('DB_USER'),
                        password=os.getenv('DB_PASS'),
                        port=os.getenv('DB_PORT'),
                        host=os.getenv('DB_HOST'),
                        service_name='XE') as db_conn:
        
        if args.create:
            create_data(db_conn)
        elif args.drop:
            drop_data(db_conn)
        else:
            raise ValueError("Invalid arguments. Must specify --create or --drop")
