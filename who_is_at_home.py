import datetime
import glob
import os.path
import sqlite3
from fastapi import FastAPI


def makequerystring_tjk():
    # Die Funktion baut aus Tagedatum und Novatime Abwesenheitsgründen eine Abfrage für die Tabelle
    # Liste_Jahreskartei auf.
    # Aus Datenschutzgründen dürfen die einzelnen Abwesenheiten nicht näher spezifiziert werden.
    heute = todays_zeitdb_field()
    nvtgruende = ['U', 'KR', 'GL', 'F', 'Sa', 'So']  # Abwesenheitsgründe in Novatime
    query = "select liste.AuswNr,kt.PersNr,kt.Name,'sonstiges' from Liste_Jahreskartei as kt,Liste_Personal as liste where liste.Name=kt.name and ("

    i = 0
    for g in nvtgruende:
        i = i + 1
        query = query + heute + " = '" + g + "'"
        if not (i == len(nvtgruende)):
            query = query + " or "
    query = query + ")"
    return query


def create_zeitdb(func_database, func_tools):
    conn = sqlite3.connect(func_database)
    c = conn.cursor()

    for datei in glob.glob(func_tools):
        with open(datei, 'r') as file:
            data = file.read().replace('\n', '')
            c.executescript(data)

    conn.commit()
    conn.close()


def todays_zeitdb_field():
    ret = 'kt.' + datetime.date.today().strftime('D%d%m')
    return ret


def whoisthere(database, tools):
    if not os.path.isfile(database):
        create_zeitdb(database, tools)
    else:
        conn = sqlite3.connect(database)
        conn.text_factory = lambda x: str(x, "latin1")
        c = conn.cursor()
        c.execute(
            "select dg.AuswNr,liste.PersNr,dg.Name,'Dienstgang' from Liste_TagesjournalaktuellaufDienstgang as dg,Liste_Personal as liste where dg.AuswNr>0 and dg.Name=liste.Name group by dg.AuswNr")
        dienstgang = c.fetchall()
        c.execute(
            "select anw.AuswNr,liste.PersNr,anw.Name,'anwesend' from Liste_Tagesjournalaktuellanwesend as anw,Liste_Personal as liste where anw.AuswNr>0 and anw.Name=liste.Name group by anw.AuswNr")
        anwesend = c.fetchall()
        c.execute(
            "select abw.AuswNr,liste.PersNr,abw.Name,'abwesend' from Liste_Tagesjournalaktuellabwesend as abw,Liste_Personal as liste where abw.AuswNr>0 and abw.Name=liste.Name group by abw.AuswNr")
        abwesend = c.fetchall()
        c.execute(makequerystring_tjk())
        kartei = c.fetchall()
        tabellen = dienstgang, anwesend, kartei, abwesend
        pnrlist = []
        zaehler = 0
        statusjson = '{"user":['
        for tab in tabellen:
            for row in tab:
                zaehler = zaehler + 1
                auswnr, pnr, name, status = row
                if len(pnr) == 6:
                    pnr = pnr + '00'
                if len(pnr) == 4:
                    pnr = '15' + pnr + '00'
                if len(pnr) == 0:
                    pnr = '99999999'
                    # fehler = fehler + 1
                if (pnr in pnrlist):
                    x = ''
                else:
                    pnrlist.append(pnr)
                    x = '{"Name" : "' + name + '", "AusweisNr" :"' + auswnr + '", "PersNr" : "' + pnr + '", "Status" :' \
                        + '"' + status + '"},'

                statusjson = statusjson + x

        statusjson = statusjson[:-1] + ']}'
        return statusjson
        conn.close()


def main():

    odatabase = 'database/novatime.s3db'
    otools = 'tools/create*.sql'
    d = whoisthere(odatabase, otools)
    print(d)

main()

print("To be continued ...")
