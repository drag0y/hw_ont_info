import re
import subprocess

def get_regtime_gpon(olt_ip, portid, onuid, snmp_com):
# --- Функция для определения времени включения ONU в сеть

    timelist = "Нет времени отключения"

    parse_data = r'STRING: "(?P<regtime>\S+ \S+)"'

    datatimeoid = "1.3.6.1.4.1.2011.6.128.1.1.2.101.1.6"
    
    datatimecmd = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {datatimeoid}.{portid}.{onuid}"
    datatimeonucmd = datatimecmd.split()

    process = subprocess.Popen(datatimeonucmd, stdout=subprocess.PIPE)
    
    while True:
        output = process.stdout.readline()

        if output == b'' and process.poll() is not None:
            break

        if output:
            outlist = output.decode('utf-8')
            match = re.search(parse_data, outlist)
            if match:
                timelist = match.group('regtime')


    datatime = timelist.replace("Z", "+03:00")


    return datatime
