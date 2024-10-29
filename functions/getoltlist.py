#!/bin/python3

import requests
import json
import ipaddress
import sqlite3

from functions.oltgetonu import snmpgetonu
from configurations.nb_conf import urlgetepon, urlgetgpon, epon_tag, gpon_tag, headers


def get_netbox_olt_list():
# --- Функция опрашивает NetBox по тегам, создаёт БД, обнуляя старую если есть.
# --- И дальше передаёт данные об ОЛТе в другие функции для опроса

    out_epon_olts = []
    out_gpon_olts = []
    outdoublemac2 = []
    outdoublesn2 = []

    nl = '\n'
# --- OIDs for get ONU list from OLT
    snmp_gpon = "1.3.6.1.4.1.2011.6.128.1.1.2.43.1.3"
    snmp_epon = "1.3.6.1.4.1.2011.6.128.1.1.2.53.1.3"

    epon = "epon"
    gpon = "gpon"

# --- SNMP community
    snmp_com = "Ciscoread1!"

# --- Подключение к БД, если таблицы уже существуют, то удаляем их
# --- При каждом опросе ОЛТов база обнуляется и заполняется заново, и там всегда актуальные данные

    conn = sqlite3.connect('onulist.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS epon")
    cursor.execute("DROP TABLE IF EXISTS gpon")
    cursor.execute("CREATE TABLE epon(number integer primary key autoincrement, maconu, portonu text, idonu text, oltip, oltname)")
    cursor.execute("CREATE TABLE gpon(number integer primary key autoincrement, snonu, portonu text, idonu text, oltip, oltname)")
    conn.close()

# --- Получениие списка Epon ОЛТов, если такие есть, то передаём их в функцию snmpgetonu 

    if epon_tag:
        response = requests.get(urlgetepon, headers=headers, verify=False)
        olts_list = json.loads(json.dumps(response.json(), indent=4))

        for parse_olts_list in olts_list["results"]:
            olt_name = []
            olt_addr = []
            olt_name = parse_olts_list["name"]
            olt_addr = ipaddress.ip_interface(parse_olts_list["primary_ip4"]["address"])
            olt_ip = str(olt_addr.ip)

            out_epon_olts.append(olt_name + " " + olt_ip)

            snmpgetonu(olt_name, olt_ip, snmp_epon, snmp_com, epon)
            

# --- Получение списка Gpon ОЛТов, если такие есть, то передаём их в функцию snmpgetonu 

    if gpon_tag:
        response = requests.get(urlgetgpon, headers=headers, verify=False)
        olts2_list = json.loads(json.dumps(response.json(), indent=4))

        for parse_olts_list in olts2_list["results"]:
            olt_name = []
            olt_addr = []
            olt_name = parse_olts_list["name"]
            olt_addr = ipaddress.ip_interface(parse_olts_list["primary_ip4"]["address"])
            olt_ip = str(olt_addr.ip)
            
            out_gpon_olts.append(olt_name + " " + olt_ip)

            snmpgetonu(olt_name, olt_ip, snmp_gpon, snmp_com, gpon)

# --- Поиск одинаковых Маков в базе

    conn = sqlite3.connect('onulist.db')
    cursor = conn.cursor()

    dubleonu = cursor.execute('select maconu, count(*) from epon group by maconu having count(*) > 1')
    dublicatemac = []
    dublicatemac2 = []

    for row in dubleonu:
        dublicatemac.append(row[0])

    if dublicatemac:
        for row in dublicatemac:
            macdoubleonu = cursor.execute(f'select * from epon where maconu glob "{row}"')
            for row in macdoubleonu:
                outdoublemac2.append(row[1] + " " + row[4])
        outdoublemac = f"Повторяющиеся ONU на EPON OLTах: {nl}{nl.join(outdoublemac2)}"

    else:
        outdoublemac = "\nНа OLTах EPON нет повторяющихся ОНУ"

# --- Поиск одинаковых серийников в базе

    dublicatesn = []
    dublicatesn2 = []
    dubleonusn = cursor.execute('select snonu, count(*) from gpon group by snonu having count(*) > 1')

    for row in dubleonusn:
        dublicatesn.append(row[0])

    if dublicatesn:
        for row in dublicatesn:
            sndoubleonu = cursor.execute(f'select * from gpon where snonu glob "{row}"')
            for row in sndoubleonu:
                outdoublesn2.append(row[1] + " " + row[4])
        outdoublesn = f"Повторяющиеся ONU на GPON OLTах: {nl}{nl.join(outdoublesn2)}"

    else:
        outdoublesn = "\nНа OLTах GPON нет повторяющихся ОНУ"


    conn.close()

    return outdoublemac, outdoublesn, out_epon_olts, out_gpon_olts


