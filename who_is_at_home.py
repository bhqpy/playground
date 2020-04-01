from pylite.simplite import Pylite
import glob
import os.path
database = 'database/dbname.sqlite'
tools = 'tools/*.sql'


def createDB(func_database, func_tools):
    db = Pylite(func_database)
    datei = []

    for datei in glob.glob(func_tools):
        with open(datei, 'r') as file:
            data = file.read().replace('\n', '')
            db.query(data)

    db.close_connection()

if not os.path.isfile(database):

    createDB(database, tools)
else:
    print ("To be continued ...")


