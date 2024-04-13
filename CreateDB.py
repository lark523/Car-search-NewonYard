""" This class creates a database if one does not exist"""
import sqlite3

class CreateDB:
    def __init__(self, name):
        self.name = name
        self.conn = sqlite3.connect(self.name +'.sqlite')
        self.cur = self.conn.cursor()

    #Create a new db with the name provided
    def dbInitialize(self):


        self.cur.executescript('''
        DROP TABLE IF EXISTS Cars;

        CREATE TABLE Cars (
            id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            make            TEXT,
            model           TEXT,
            year            INTEGER,
            location        TEXT,
            yard_date       INTEGER,
            vin             INTEGER NOT NULL UNIQUE

        );
        ''')

    # Return the name of the sqlite db    
    def dbName(self):
        return self.name
