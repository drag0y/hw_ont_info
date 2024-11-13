import subprocess
import sqlite3

from functions.epon.get_level_epon import get_level_epon
from functions.epon.get_lan_state_epon import get_lanstate_epon
from functions.epon.get_lastdown_epon import get_lastdown_epon
from functions.epon.get_timedown_epon import get_downtime_epon
from functions.epon.get_timeup_epon import get_regtime_epon
from functions.epon.get_eponlevel_tree import get_epon_level_tree


def get_level_onu(usermaconu, snmp_com, tree=False):
# Функция для определения состояния ОНУ и вызова функций для запроса дополнительных данных
    

    # ---- Подключение к базе и поиск ONU

    conn = sqlite3.connect('onulist.db')
    cursor = conn.cursor()
    findonu = cursor.execute(f'select * from epon where maconu glob "{usermaconu}"')

    for onuinfo in findonu:
        portid = onuinfo[2]
        onuid = onuinfo[3]
        olt_ip = onuinfo[4]
        olt_name = onuinfo[5]    

    if tree == False:

        # ---- Состояние ОНУ

        lastdownoid = "1.3.6.1.4.1.2011.6.128.1.1.2.57.1.15"
        lastdowncmd = f"snmpwalk -c {snmp_com} -v2c {olt_ip} {lastdownoid}.{portid}.{onuid}"
        lastdowncmd2 = lastdowncmd.split()

        process = subprocess.Popen(lastdowncmd2, stdout=subprocess.PIPE)
        data = process.communicate(timeout=5)
        data2 = data[-2].decode('utf-8')
        onu_state = data2.split()

        # ---- Если ONU в сети, то для опроса вызываем следующие функции
        if onu_state[-1] == '1':
            onustate = "В сети"
            lan_out = get_lanstate_epon(olt_ip, portid, onuid, snmp_com) # Состояние LAN порта
            uptime = get_regtime_epon(olt_ip, portid, onuid, snmp_com) # Время последней регистрации в сети
            lastdownonu = get_lastdown_epon(olt_ip, portid, onuid, snmp_com) # Причина последнего отключения
            datatime = get_downtime_epon(olt_ip, portid, onuid, snmp_com) # Время последнего отключения
            level_onu, level_olt = get_level_epon(olt_ip, portid, onuid, snmp_com) # Уровень сигнала
            outinformation = (f"""ONU найдена на OLTе: {olt_name}\n
Состояние ONU: {onustate}
Статус LAN порта: {lan_out}
Время включения: {uptime}
Время последнего отключения: {datatime}
Причина последнего отключения: {lastdownonu}
Уровень сигнала с ОЛТа:  {level_onu}
Уровень сигнала с ОНУ:   {level_olt}
""")

        # ---- Если ONU не в сети, то вызываем следующие фуункции
        elif onu_state[-1] == '2':
            onustate = "Не в сети"
            datatime = get_downtime_epon(olt_ip, portid, onuid, snmp_com) # Время последнего отключения
            lastdownonu = get_lastdown_epon(olt_ip, portid, onuid, snmp_com) # Причина последнего отключения
            outinformation = (f"""ONU найдена на OLTе: {olt_name}\n
Состояние ONU: {onustate}
Время отключения: {datatime}
Причина отключения: {lastdownonu}
""")
        # ---- Если состояние ONU определить не удалось
        else:
            outinformation = "Состояние ONU: Не удалось определить"

    elif tree == True:
        outinformation = get_epon_level_tree(olt_ip, portid, snmp_com)

    conn.close()


    return outinformation


# ---- Конец Функции

