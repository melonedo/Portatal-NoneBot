import asyncio, aiohttp
import database

from nonebot import on_command, get_driver, on_notice
from nonebot.adapters import Message, Event, Bot
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import PokeNotifyEvent

driver = get_driver()
http_session = None


@driver.on_shutdown
async def shutdown_session():
    if http_session:
        await http_session.close()

async def query_electricity_db(qq, room: str) -> str:
    """如果room是None，则查找最近一次查找的房间，否则按照room查找并更新查找信息"""
    set_room = False
    if not room:
        room = database.get_last_room(qq)
    if not room:
        return "没有查询记录，请先用“电费 房间号”的格式查找以记录。嘉定友园格式如“电费 12-345”，四平格式为“电费 西南一2345”。"
    else:
        set_room = True

    global http_session
    if not http_session:
        http_session = aiohttp.ClientSession()
    # async with app.http_session.get("https://elec.miaotony.xyz/electricity", params={"room": room}) as resp:
    async with http_session.get("http://localhost:4312/electricity", params={"room": room}) as resp:
        data = await resp.json()
    if data["success"]:
        if set_room:
            database.set_last_room(qq, room)
        return f"""{data["name"]} {data["type"]}: {data["number"]}{data["unit"]}"""
    else:
        return f"""查询失败：{data["error"]}"""


elec = on_command("电费")
@elec.handle()
async def reply_elec(evt: Event, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    print(evt.get_user_id())
    reply = await query_electricity_db(evt.get_user_id(), msg)
    await elec.finish(reply)


def _poke_check(event:PokeNotifyEvent):
        return event.target_id==event.self_id
        
poke = on_notice(rule=_poke_check)
@poke.handle()
async def handle_poke(evt: PokeNotifyEvent):
    reply = await query_electricity_db(evt.get_user_id(), "")
    await elec.finish(reply)

