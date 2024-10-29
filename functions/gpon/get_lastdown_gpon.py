import subprocess

def get_lastdown_gpon(olt_ip, portid, onuid, snmp_com):
# --- Функция определения причины отключения ONU из сети

    lastdownoid = "1.3.6.1.4.1.2011.6.128.1.1.2.46.1.24"
    lastdowncmd = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {lastdownoid}.{portid}.{onuid}"
    lastdowncmd2 = lastdowncmd.split()

    process = subprocess.Popen(lastdowncmd2, stdout=subprocess.PIPE)
    data = process.communicate(timeout=5)
    data2 = data[-2].decode('utf-8')
    last_down_onu = data2.split()

    if last_down_onu[-1] == '13':
        lastdownonu = "Power-Off"
    elif last_down_onu[-1] == '1' or '2':
        lastdownonu = "LOS"
    else:
        lastdownonu = "Не удалось определить"

    return lastdownonu
