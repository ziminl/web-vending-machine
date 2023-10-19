import sqlite3
import discord
import setting
client = discord.Client()
@client.event
async def on_ready():
    print(client.guilds)
    for guild in client.guilds:
        id = guild.id
        try:
            con = sqlite3.connect(f"../DB/{id}.db")
            cur = con.cursor()
            #migration code here
            try:
                cur.execute("ALTER TABLE serverinfo ADD culture_fee INTEGER DEFAULT 10 not null")
                print(f"{id}: 컬쳐랜드 수수료 마이그래이션 성공")
            except Exception as e:
                print(f"{id}: 컬쳐랜드 수수료 마이그래이션 실패(이미 한 경우 일수도), {e}")
            try:
                cur.execute("ALTER TABLE serverinfo ADD bank TEXT")
                print(f"{id}: 은행정보 마이그래이션 성공")
            except Exception as e:
                print(f"{id}: 은행정보 마이그래이션 실패(이미 한 경우 일수도), {e}")
            con.commit()
            con.close()
        except Exception as e:
            print(f"{id}: 마이그레이션 실패, {e}")
client.run(setting.token)

