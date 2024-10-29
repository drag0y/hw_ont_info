import subprocess

def get_catvstate_gpon(olt_ip, portid, onuid, snmp_com):
# --- Функция для получения состояния CATV порта, включен или выключен в конфигурации
    try:
        catvstatusoid = "1.3.6.1.4.1.2011.6.128.1.1.2.63.1.2"
        catvstatcmd = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {catvstatusoid}.{portid}.{onuid}"
        catvstatuscmd = catvstatcmd.split()

        process = subprocess.Popen(catvstatuscmd, stdout=subprocess.PIPE)
        data = process.communicate(timeout=2)
        data2 = data[-2].decode('utf-8')
        catvstatus = data2.split()

        if catvstatus[-1] == '1':
            catv_out = "ON"
        elif catvstatus[-1] == '2':
            catv_out = "OFF"
        else:
            catv_out = "Не удалось определить"

    except subprocess.TimeoutExpired:
        catv_out = "Не удалось определить"

    return catv_out
