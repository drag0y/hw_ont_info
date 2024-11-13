import sqlite3
import re
import subprocess

def get_gpon_level_tree(olt_ip, portid, snmp_com):
# --- Функция получения уровней сигнала 

    out_tree = ""
    out_tree2 = []
    tree_in = []
    tree_out = []
    onulist = []
    level_rx = ""
    level_tx = ""

    snmp_rx_onu = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4"
    snmp_rx_olt = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6"

    parse_tree = r'(\d+){10}.(?P<onuid>\S+) .+(?P<treelevel>-\S+)'

    # ---- Ищем в базе серийник ОНУ для сопоставления с индексами

    onureplace = {}

    conn = sqlite3.connect('onulist.db')
    cursor = conn.cursor()

    onureplace_in = cursor.execute(f'SELECT * FROM gpon WHERE oltip="{olt_ip}" AND portonu="{portid}";')
    for onu in onureplace_in:
        indexonu_out = onu[3]
        snonu_out = onu[1]

        onureplace.setdefault(indexonu_out)
        onureplace.update({indexonu_out: snonu_out})

    # ---- Получение уровня сигнала с ОНУ
    cmd_rx_onu = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {snmp_rx_onu}.{portid}"
    cmd = cmd_rx_onu.split()

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)


    while True:
        output = process.stdout.readline()

        if output == b'' and process.poll() is not None:
            break

        if output:
            outlist = output.decode('utf-8')
            match = re.search(parse_tree, outlist)
            if match:
                onuid = match.group('onuid')
                level = match.group('treelevel')
                level_rx = int(level)/100

                onulist.append(onuid)
                tree_in.append(level_rx)

    # ---- Получение результата уровня в сторону ОЛТа
    parse_tree_sn = r'(\d+){10}.(?P<onuid>\S+) .+INTEGER: (?P<treelevel>\d+)'
    
    cmd_rx_olt = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {snmp_rx_olt}.{portid}"
    cmd = cmd_rx_olt.split()

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    while True:
        output = process.stdout.readline()

        if output == b'' and process.poll() is not None:
            break

        if output:
            outlist = output.decode('utf-8')
            match = re.search(parse_tree_sn, outlist)
            if match:
                onuid = match.group('onuid')
                level = match.group('treelevel')
                
                if len(level) == 4:
                    level_tx2 = int(level)/100-100
                    level_tx = format(level_tx2, '.2f')
                
                    tree_out.append(level_tx)
    
    # ----
    nl = "\n"
    for i in range(len(onulist)):
        onusn = str(onulist[i])
        out_tree2.append(onureplace[onusn] + " " * 8 + str(tree_in[i]) + " " * 8 + str(tree_out[i]))
    out_tree = f"SN                #    IN    #    OUT: {nl}{nl.join(out_tree2)}"

    conn.close()

    return out_tree

