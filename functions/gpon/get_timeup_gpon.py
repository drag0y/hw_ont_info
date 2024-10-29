import subprocess

def get_regtime_gpon(olt_ip, portid, onuid, snmp_com):
# --- Функция для определения времени включения ONU в сеть

    datatimeoid = "1.3.6.1.4.1.2011.6.128.1.1.2.101.1.6"
    id = 9
    datatimecmd = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {datatimeoid}.{portid}.{onuid}.{id}"
    datatimeonucmd = datatimecmd.split()

    process = subprocess.Popen(datatimeonucmd, stdout=subprocess.PIPE)
    data = process.communicate(timeout=2)
    data2 = data[-2].decode('utf-8')
    downonu = data2.split()
    downdata = downonu[-2]

    while (downdata in "this" or downdata in "=") and id > 0:
        id = id - 1
        datatimecmd = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {datatimeoid}.{portid}.{onuid}.{id}"
        datatimeonucmd = datatimecmd.split()
        process = subprocess.Popen(datatimeonucmd, stdout=subprocess.PIPE)
        data = process.communicate(timeout=2)
        data2 = data[-2].decode('utf-8')
        downonu = data2.split()
        downdata = downonu[-2]

    downdata = downonu[-2]
    downtime = downonu[-1].replace("Z", "+03:00")
    datatime = f"{downdata} {downtime}"


    return datatime
