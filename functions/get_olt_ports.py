#!/bin/python3

import re
import sqlite3
import subprocess
from contextlib import redirect_stdout


def snmpgetports(olt_name, olt_ip, snmp_com):

# --- Функция для запроса портов

    snmp_oid = "1.3.6.1.2.1.31.1.1.1.1"

    parseout = r'(?P<portoid>\d{10}).+ (?P<ponport>\d+\/\d+\/\d+)'

    conn = sqlite3.connect('onulist.db')
    cursor = conn.cursor()

    query_ports = "INSERT into ponports(oltip, oltname, ponport, portoid) values (?, ?, ?, ?)"

# --- Команда опроса OLTа

    process = subprocess.Popen(['snmpwalk', '-c', snmp_com, '-v2c', olt_ip, snmp_oid], stdout=subprocess.PIPE)
    listont = []

# --- Парсинг Мак адресов и добавление в базу

    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            outlist = output.strip().decode('utf-8')
            match = re.search(parseout, outlist)
            if match: 
                portlist = olt_ip, olt_name, match.group('ponport'), match.group('portoid')
                cursor.execute(query_ports, portlist)


    conn.commit()
    conn.close()


# --- end

