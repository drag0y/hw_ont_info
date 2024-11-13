from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command

from functions.eponlevel import get_level_onu
from functions.gponlevel import get_level_onu_sn

from configurations.tgbotconf import USERS # Access permit of Users
from functions.getoltlist import get_netbox_olt_list # function to get olt list and call function to get onu list


user_private_router = Router()

snmp_gpon = "1.3.6.1.4.1.2011.6.128.1.1.2.43.1.3"
snmp_epon = "1.3.6.1.4.1.2011.6.128.1.1.2.53.1.3"

snmp_com = "Ciscoread1!"


start_message = """
Для просмотра состояния ONU
введите мак адрес или серийный номер ONU.

Для просмотра уровней с дерева
введите команду /tree и через пробел
мак или серийник ону.

Если ONU не найдена, попробуйте опросить OLTы.
Для опроса OLTов введите команду /oltsupdate
А затем попробуйте ещё раз."""


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    if message.from_user.id in USERS:
        await message.answer(start_message)
    else:
        await message.answer(f"Вас нет в списке разрешённых пользователей. Ваш ID {message.from_user.id}")

@user_private_router.message(Command('oltsupdate'))
async def start_gel_olt(message: types.Message):

    if message.from_user.id in USERS:
        await message.answer("""Начат опрос OLTов, дождитесь сообщение о завершении!
Процесс занимает примерное пару минут.""")
        outdoublemac, outdoublesn, out_epon_olts, out_gpon_olts = get_netbox_olt_list()
        nl = '\n'
        await message.answer(f"""
Опрос OLTов завершён
{nl}Список опрошенных OLTов:
    EPON:{nl}{nl.join(out_epon_olts)}
    GPON:{nl}{nl.join(out_gpon_olts)}
""")
        await message.answer(f"{outdoublemac}")
        await message.answer(f"{outdoublesn}")
        

    else:
        await message.answer(f"Вас нет в списке разрешённых пользователей. Ваш ID {message.from_user.id}")


@user_private_router.message(Command('tree'))
async def menu_cmd(message: types.Message):
    if message.from_user.id in USERS:
        try:
            user_input = message.text.split()
            usermac_in = user_input[1]
            usersn_in = user_input[1]

            usermaconu = usermac_in.lower().replace(":", "").replace(" ", "")
            usersnonu = usersn_in.lower().replace(" ", "")

            if len(usermaconu) == 12:
                await message.answer(f"Ищем ONU с маком {usermaconu}")
                out_tree_info = get_level_onu(usermaconu, snmp_com, True)
                await message.answer(f"{out_tree_info}")

    
            elif len(usersnonu) == 16:
                await message.answer(f"Ищем ONU с серийником {usersnonu}")
                out_tree_info = get_level_onu_sn(usersnonu, snmp_com, True)
                await message.answer(f"{out_tree_info}")

            else:
                await message.answer(f"Неправильный Мак или Серийник ONU!")


        except UnboundLocalError:
            await message.answer(f"ONU {usermaconu} не найдена!")
        except IndexError:
            await message.answer("Ошибка синтаксиса!")
        except KeyError:
            await message.answer("Разное кол-во ONU в дереве и в базе. База устарела, необходимо опросить OLTы. /oltsupdate")

    else:
        await message.answer(f"Вас нет в списке разрешённых пользователей. Ваш ID {message.from_user.id}")

@user_private_router.message(F.text)
async def menu_cmd(message: types.Message):
    if message.from_user.id in USERS:
        try:
            user_input = message.text
            usermac_in = user_input
            usersn_in = user_input

            usermaconu = usermac_in.lower().replace(":", "").replace(" ", "")
            usersnonu = usersn_in.lower().replace(" ", "")

            if len(usermaconu) == 12:
                await message.answer(f"Ищем ONU с маком {usermaconu}")
                out_info = get_level_onu(usermaconu, snmp_com)
                await message.answer(f"{out_info}")

    
            elif len(usersnonu) == 16:
                await message.answer(f"Ищем ONU с серийником {usersnonu}")
                out_info = get_level_onu_sn(usersnonu, snmp_com)
                await message.answer(f"{out_info}")

            else:
                await message.answer("Неправильный Мак или Серийник ONU!")


        except UnboundLocalError:
            await message.answer(f"ONU {usermaconu} не найдена!")
        except IndexError:
            await message.answer("Ошибка синтаксиса!")

    else:
        await message.answer(f"Вас нет в списке разрешённых пользователей. Ваш ID {message.from_user.id}")

