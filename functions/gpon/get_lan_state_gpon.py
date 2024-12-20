import subprocess

def get_lanstate_gpon(olt_ip, portid, onuid, snmp_com):
# --- Функция для получения состояния LAN порта
    try:
        ethstatusoid = "1.3.6.1.4.1.2011.6.128.1.1.2.62.1.22"
        ethstatcmd = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {ethstatusoid}.{portid}.{onuid}.1"
        ethstatuscmd = ethstatcmd.split()

        process = subprocess.Popen(ethstatuscmd, stdout=subprocess.PIPE)
        data = process.communicate(timeout=5)
        data2 = data[-2].decode('utf-8')
        lanstatus = data2.split()

        if lanstatus[-1] == '1':
            lan_out = "UP"
        elif lanstatus[-1] == '2':
            lan_out = "DOWN"
        else:
            lan_out = "Не удалось определить"

    except subprocess.TimeoutExpired:
        lan_out = "Не удалось определить"

    return lan_out
