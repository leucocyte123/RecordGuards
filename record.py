# -*- coding: utf-8 -*-
import getpass

import asyncio
import mysql.connector

from blivedm.blivedm import BLiveClient, GuardBuyMessage

VtuberOfInterest = {
    'xuehusang': 24393,
    'kitzuki': 22889484,
}
_level_to_text = {
    0: '非舰长', 
    1: '总督', 
    2: '提督', 
    3: '舰长'
}

selected_vtuber = 'kitzuki'
room_id = VtuberOfInterest[selected_vtuber]

mysqlHost = '172.17.0.4'
mysqlUsername = 'root'
mysqlPassword = ''

def inputMysqlPassword():
    global mysqlPassword
    mysqlPassword = getpass.getpass(prompt='MySQL Password: ')

def parseMessage(message: GuardBuyMessage):
    id = '%s-%d' % (message.uid, message.end_time)
    uname = message.username
    uid = message.uid
    level = _level_to_text[message.guard_level]
    count = message.num
    return id, uname, uid, level, count

def writeMySQL(val):
    mydb = mysql.connector.connect(
        host=mysqlHost,
        user=mysqlUsername,
        password=mysqlPassword,
        database=selected_vtuber
    )
    mycursor = mydb.cursor()

    sql = "INSERT INTO guards (id, uname, uid, level, count) VALUES (%s, %s, %s, %s, %s)"

    mycursor.execute(sql, val)
    mydb.commit()

class AutovipClient(BLiveClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = kwargs['label']

    async def _on_buy_guard(self, message: GuardBuyMessage):
        val = parseMessage(message)
        writeMySQL(val)
        print(f'{message.username} 购买{message.gift_name}')

async def main():
    client = AutovipClient(room_id, ssl=True)
    future = client.start()
    try:
        await future
    finally:
        await client.close()

if __name__ == '__main__':
    inputMysqlPassword()
    asyncio.get_event_loop().run_until_complete(main())