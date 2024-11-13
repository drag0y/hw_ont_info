import subprocess
import sqlite3

from functions.gpon.get_level_gpon import get_level_gpon
from functions.gpon.get_lan_state_gpon import get_lanstate_gpon
from functions.gpon.get_lastdown_gpon import get_lastdown_gpon
from functions.gpon.get_timedown_gpon import get_downtime_gpon
from functions.gpon.get_timeup_gpon import get_regtime_gpon
from functions.gpon.get_catv_state_gpon import get_catvstate_gpon
from functions.gpon.get_gponlevel_tree import get_gpon_level_tree

def get_level_onu_sn(usersnonu, snmp_com, tree=False):
# ---- Функция определения состояния ОНУ и вызова функций для запроса дополнительных данных

   
# ---- Подключение к базе и поиск ONU

    conn = sqlite3.connect('onulist.db')
    cursor = conn.cursor()
    findonu = cursor.execute(f'select * from gpon where snonu glob "{usersnonu}"')
    for onuinfo in findonu:
        portid = onuinfo[2]
        onuid = onuinfo[3]
        olt_ip = onuinfo[4]
        olt_name = onuinfo[5]
    
    gponportonu = cursor.execute(f'SELECT gponport FROM gponports WHERE oltip="{olt_ip}" AND portoid="{portid}";')
    
    portonu_out = "Не удалось определить порт"
    for portonu in gponportonu:
        portonu_out = portonu[0]

    if tree == False:
    # ---- Состояние ОНУ

        lastdownoid = "1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15"
        lastdowncmd = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {lastdownoid}.{portid}.{onuid}"
        lastdowncmd2 = lastdowncmd.split()

        process = subprocess.Popen(lastdowncmd2, stdout=subprocess.PIPE)
        data = process.communicate(timeout=5)
        data2 = data[-2].decode('utf-8')
        onu_state = data2.split()

# ---- Если ONU в сети, то для опроса вызываем следующие функции
        if onu_state[-1] == '1': 
            onustate = "В сети"
            lan_out = get_lanstate_gpon(olt_ip, portid, onuid, snmp_com) # Состояние LAN порта
            catv_out = get_catvstate_gpon(olt_ip, portid, onuid, snmp_com) # Состояние CATV порта
            uptime = get_regtime_gpon(olt_ip, portid, onuid, snmp_com) # Время последней регистрации в сети
            lastdownonu = get_lastdown_gpon(olt_ip, portid, onuid, snmp_com) # Причина последнего отключения
            datatime = get_downtime_gpon(olt_ip, portid, onuid, snmp_com) # Время последнего отключения
            level_onu, level_olt = get_level_gpon(olt_ip, portid, onuid, snmp_com) # Уровень сигнала
            outinformation = (f"""ONU найдена на OLTе: {olt_name}
Порт: {portonu_out} {onuid}

Состояние ONU: {onustate}
Статус LAN порта: {lan_out}
Статус CATV порта: {catv_out}
Время включения: {uptime}
Время последнего отключения: {datatime}
Причина последнего отключения: {lastdownonu}
Уровень сигнала с ОЛТа:  {level_onu}
Уровень сигнала с ОНУ:   {level_olt}
""")

# ---- Если ONU не в сети, то вызываем следующие фуункции
        elif onu_state[-1] == '2':
            onustate = "Не в сети"
            datatime = get_downtime_gpon(olt_ip, portid, onuid, snmp_com) # Время последнего отключения
            lastdownonu = get_lastdown_gpon(olt_ip, portid, onuid, snmp_com) # Причина последнего отключения
            outinformation = (f"""ONU найдена на OLTе: {olt_name}\n
Состояние ONU: {onustate}
Время отключения: {datatime}
Причина отключения: {lastdownonu}
""")
# ---- Если состояние ONU определить не удалось
        else:
            outinformation = "Состояние ONU: Не удалось определить"    

    elif tree == True:
        outinformation = get_gpon_level_tree(olt_ip, portid, snmp_com)

    conn.close()


    return outinformation


# ---- Конец Функции

