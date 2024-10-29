#!/bin/python3

from pprint import pprint
import re
import sqlite3
import subprocess
from contextlib import redirect_stdout


def snmpgetonu(olt_name, olt_ip, snmp_oid, snmp_com, port_type):

# --- Функция для запроса списка зареганых ONU и парсинг

    parseout = r'(?P<portonu>\d{10}).(?P<onuid>\d+)=\S+:(?P<maconu>\S+)'
    parseoutsn = r'(?P<portonu>\d{10}).(?P<onuid>\d+)=(\S+:["]|\S+:)(?P<snonu>\S+(?=")|\S+)'

    conn = sqlite3.connect('onulist.db')

    cursor = conn.cursor()


    query = "INSERT into epon(maconu, portonu, idonu, oltip, oltname) values (?, ?, ?, ?, ?)"
    querygpon = "INSERT into gpon(snonu, portonu, idonu, oltip, oltname) values (?, ?, ?, ?, ?)"

# --- Команда опроса OLTа

    process = subprocess.Popen(['snmpwalk', '-c', snmp_com, '-v2c', olt_ip, snmp_oid], stdout=subprocess.PIPE)
    listont = []

# --- Парсинг Мак адресов и добавление в базу

    if port_type == "epon":

        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                outlist = output.strip().decode('utf-8').replace(" ", "").lower()
                match = re.search(parseout, outlist)
            
                listont = match.group('maconu'), match.group('portonu'), match.group('onuid'), olt_ip, olt_name
                print(listont)
                cursor.execute(query, listont)


        conn.commit()
        conn.close()


# --- Парсинг серийников и добавление в базу

    if port_type == "gpon":
        try:
            while True:
                output = process.stdout.readline()
                if output == b'' and process.poll() is not None:
                    break
                if output:
                    outlist = output.strip().decode('utf-8').replace(" ", "").replace("\\", "")
                    match = re.search(parseoutsn, outlist)
 
                    if match:          
                        print(match.group(0))
                        if len(match.group('snonu')) == 16:
                            listont = match.group('snonu').lower(), match.group('portonu'), match.group('onuid'), olt_ip, olt_name
                            cursor.execute(querygpon, listont)
                   

                        elif len(match.group('snonu')) < 16:
                            listont = match.group('snonu').encode().hex(), match.group('portonu'), match.group('onuid'), olt_ip, olt_name
                            cursor.execute(querygpon, listont)
                    
                    print(listont)
                  

        except ValueError:
            print("Кривая ONU")

        conn.commit()
        conn.close()

# --- end
