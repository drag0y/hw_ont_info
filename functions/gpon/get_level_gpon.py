import subprocess

def get_level_gpon(olt_ip, portid, onuid, snmp_com):
# ---- Функция определения уровней сигналов ОНУ

    snmp_rx_onu = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4"
    snmp_rx_olt = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6"

    cmd_rx_onu = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {snmp_rx_onu}.{portid}.{onuid}"
    cmd = cmd_rx_onu.split()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    data = process.communicate(timeout=5)
    data2 = data[-2].decode('utf-8')
    rx_onu = data2.split()
    level_onu = int(rx_onu[-1])/100

# ---- Вывод результата уровня с ОЛТа

    cmd_rx_olt = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {snmp_rx_olt}.{portid}.{onuid}"
    cmd = cmd_rx_olt.split()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    data = process.communicate(timeout=5)
    data2 = data[-2].decode('utf-8')
    rx_olt = data2.split()
    level_olt = int(rx_olt[-1])/100-100

    return level_onu, format(level_olt, '.2f')
