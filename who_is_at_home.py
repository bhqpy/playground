import glob
import os.path
import sqlite3
import datetime


database = 'database/novatime.s3db'
tools = 'tools/create*.sql'


def createZeitDB(func_database, func_tools):
    conn = sqlite3.connect(func_database)
    c = conn.cursor()
    datei = []

    for datei in glob.glob(func_tools):
        with open(datei, 'r') as file:
            data = file.read().replace('\n', '')
            c.executescript(data)

    conn.commit()
    conn.close()

def todays_zeitDB_field():
    return datetime.date.today().strftime('D%d%m')

# End of definitions
if not os.path.isfile(database):

    createZeitDB(database, tools)
else:
    conn = sqlite3.connect(database)
    conn.text_factory = lambda x: str(x, "latin1")
    c = conn.cursor()
    c.execute("select * from Liste_Tagesjournalaktuellanwesend where AuswNr>1")

    anwesend = c.fetchall()
    c.execute("select * from Liste_Tagesjournalaktuellabwesend where AuswNr>1")
    abwesend = c.fetchall()
    c.execute("select PersNr,Name,D2302 from Liste_Jahreskartei where PersNr > 1")
    kartei = c.fetchall()
    conn.close()
    print(anwesend)
    print(abwesend)
    print(kartei)
    print(todays_zeitDB_field())
    print("To be continued ...")
