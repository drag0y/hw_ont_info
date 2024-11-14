import sqlite3
import re
import subprocess

def getgpontreestatus(olt_ip, portid, snmp_com):
# --- Функция получения уровней сигнала 

    onulist = []
    statuslist = []
    downlist = []

    out_tree = ""
    out_tree2 = []
    onustatus = ""
    downcose = ""


    oid_state = "1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15"
    oid_cose = "1.3.6.1.4.1.2011.6.128.1.1.2.46.1.24"

    parse_state = r'(\d+){10}.(?P<onuid>\S+) .+INTEGER: (?P<onustate>\d+|-\d+)'
    parse_down = r'(\d+){10}.(?P<onuid>\S+) .+INTEGER: (?P<downcose>\d+|-\d+)'


    # ---- Ищем в базе маке ОНУ для сопоставления с индексами
    onureplace = {}

    conn = sqlite3.connect('onulist.db')
    cursor = conn.cursor()

    onureplace_in = cursor.execute(f'SELECT * FROM gpon WHERE oltip="{olt_ip}" AND portonu="{portid}";')
    for onu in onureplace_in:
        indexonu_out = onu[3]
        snonu_out = onu[1]

        onureplace.setdefault(indexonu_out)
        onureplace.update({indexonu_out: snonu_out})

    # ---- Получение статуса с дерева
    cmd_onu_state = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {oid_state}.{portid}"
    cmd = cmd_onu_state.split()

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)


    while True:
        output = process.stdout.readline()

        if output == b'' and process.poll() is not None:
            break

        if output:
            outlist = output.decode('utf-8')
            match = re.search(parse_state, outlist)
            if match:
                onuid = match.group('onuid')
                onustatus = match.group('onustate')
                onustatus = onustatus.replace("1", "ONLINE").replace("2", "OFFLINE").replace("-1", "OFFLINE")

                onulist.append(onuid)
                statuslist.append(onustatus)


    # ---- Получение причины отключения ONU
    cmd_down_cose = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {oid_cose}.{portid}"
    cmd = cmd_down_cose.split()

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)


    while True:
        output = process.stdout.readline()

        if output == b'' and process.poll() is not None:
            break

        if output:
            outlist = output.decode('utf-8')
            match = re.search(parse_down, outlist)
            if match:
                downcose = match.group('downcose')
                downcose = downcose.replace("13", "POWER-OFF").replace("2", "LOS").replace("1", "LOS")
                downlist.append(downcose)
    
    # ----
    nl = "\n"
    for i in range(len(onulist)):
        onusn = str(onulist[i])
        onudown = str(downlist[i])
        if statuslist[i] == "OFFLINE":
            statuslist[i] = statuslist[i].replace("OFFLINE", onudown)
        out_tree2.append(str(onureplace[onusn]) + " | " + str(statuslist[i]))
    out_tree = f"SN            #    Stats: {nl}{nl.join(out_tree2)}"

    conn.close()
    
    return out_tree

