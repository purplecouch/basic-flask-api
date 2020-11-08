# A simple script to transfer the contents of a csv file into a .db file using sqlite.

import csv
import sqlite3
from sqlite3 import Error
import pandas as pd
import time


def create_connection(database):
    """ 
    Function that creates a connection to a sqlite3 database file.
    @param database -- The path and name of the database file to connect to.
    """
    conn = None
    try:
        print("----------Attempting to connect to database using Sqlite3 version {version} ...".format(version = sqlite3.version))
        conn = sqlite3.connect(database)
        print("----------Successfully to connected to {database}".format(database = database))

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def xlsx_to_db(file, database, table):
    conn = sqlite3.connect(database)

    print('reading file {}'.format(file))
    df = pd.read_excel(file)
    shape = df.shape
    row_count = shape[0]
    column_count = shape[1]
    print('row count: ', row_count)
    print('column count', column_count)
    print('load data to {}'.format(table))
    df.to_sql(table, conn, if_exists = "replace", index = False)

    print('reading table..')

    df2 = pd.read_sql("select * from {} limit 1".format(table),conn)
    df2_rows = pd.read_sql("select count(*) from {}".format(table),conn)
    shape2 = df2.shape
    tbl_column_count = shape2[1]
    print('table row count: ')
    print(df2_rows)
    print('table column count', tbl_column_count)

def viewDatabaseTable(database, table):
    conn = sqlite3.connect(database)
    curs = conn.cursor()
    curs.execute("SELECT * FROM {} limit 5".format(table))
    rows = curs.fetchall()
    for row in rows:
        print(row)

def main():
    start = time.time()
    create_connection("h1b.db")
    xlsx_to_db("H-1B_Disclosure_Data_FY2018_EOY.xlsx", "h1b.db", "h1b_data", )
    end = time.time()
    runtime = end - start
    print('runtime (seconds): ',runtime)
    


if __name__ == '__main__':
    main()