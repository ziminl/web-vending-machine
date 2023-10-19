import asyncio
import discord
import sqlite3
import requests
import os
import json
import setting
import randomstring
import datetime
from datetime import timedelta
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
import traceback
import aiohttp

'''
마이그레이션
모든 서버 DB에 
cur.execute("ALTER TABLE serverinfo ADD culture_fee INTEGER DEFAULT 10 not null")
cur.execute("ALTER TABLE serverinfo ADD bank TEXT")
실행
'''

client = discord.Client()

eb = discord.Embed

token = setting.token

master_ids = [584977475461971984]
def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True

def get_expiretime(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        how_long = (ExpireTime - ServerTime)
        days = how_long.days
        hours = how_long.seconds // 3600
        minutes = how_long.seconds // 60 - hours * 60
        return str(round(days)) + "일 " + str(round(hours)) + "시간 " + str(round(minutes)) + "분" 
    else:
        return False

def prime_number(number):
    if number != 1:                 
        for f in range(2, number):  
            if number % f == 0:     
                return False
    else:
        return False
    return True

def make_expiretime(days):
    ServerTime = datetime.datetime.now()
    ExpireTime = ServerTime + timedelta(days=days)
    ExpireTime_STR = (ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def add_time(now_days, add_days):
    ExpireTime = datetime.datetime.strptime(now_days, '%Y-%m-%d %H:%M')
    ExpireTime_STR = (ExpireTime + timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def nowstr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def embed(embedtype, embedtitle, description):
    if (embedtype == "error"):
        return discord.Embed(color=0xff0000, title=":no_entry: " + embedtitle, description=description)
    if (embedtype == "success"):
        return discord.Embed(color=0x00ff00, title=":white_check_mark: " + embedtitle, description=description)
    if (embedtype == "warning"):
        return discord.Embed(color=0xffff00, title=":warning: " + embedtitle, description=description)
    if (embedtype == "loading"):
        return discord.Embed(color=0x808080, title=":gear: " + embedtitle, description=description)
    if (embedtype == "primary"):
        return discord.Embed(color=0x808080, title=embedtitle, description=description)

def get_logwebhk(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT logwebhk FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    return data

def get_buylogwebhk(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT buylogwebhk FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    return data

def get_roleid(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT roleid FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    if (str(data).isdigit()):
        return int(data)
    else:
        return data

@client.event
async def on_ready():
    print(f"Login: {client.user}\nInvite Link: https://discord.com/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.author.id in master_ids:
        if (message.content.startswith("!생성 ")):
            try:
                create_amount = int(message.content.split(" ")[1])
                if (create_amount <= 0 or create_amount > 10):
                    raise TypeError
            except:
                await message.channel.send("라이센스를 만들 수 없습니다.\n1~10의 숫자를 입력하세요.")
                return
            try:
                license_length = int(message.content.split(" ")[2])
                assert license_length != 0
            except:
                license_length = 30

            con = sqlite3.connect("../DB/" + "license.db")
            cur = con.cursor()
            created_licenses = []

            for n in range(create_amount):
                code = randomstring.pick(30).upper()
                cur.execute("INSERT INTO license Values(?, ?, ?, ?, ?);", (code, license_length, 0, "None", 0))
                created_licenses.append(code + f"  `{license_length}`일권")

            con.commit()
            con.close()

            await message.channel.send("**생성된 라이센스**\n" + "\n".join(created_licenses))

        if (message.content.startswith("!검색 ")):
            license_tosearch = message.content.split(" ")[1]
            con = sqlite3.connect("../DB/" + "license.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM license WHERE code == ?;", (license_tosearch,))
            search_result = cur.fetchone()
            if (search_result != None):
                if (search_result[2] != 0):
                    await message.channel.send("**라이센스 검색 결과**\n기간단위 : " + str(search_result[1]) + " 일\n사용 여부 : 사용됨\n사용 시간 : " + str(search_result[3]) + "\n사용된 서버 : " + str(search_result[4]))
                else:
                    await message.channel.send("**라이센스 검색 결과**\n기간단위 : " + str(search_result[1]) + " 일\n사용 여부 : 사용되지 않음")
            else:
                await message.channel.send("라이센스 검색 실패 : 그런 라이센스가 없음.")

        if (message.content.startswith("!삭제 ")):
            license_todel = message.content.split(" ")[1:]
            con = sqlite3.connect("../DB/" + "license.db")
            cur = con.cursor()
            for license_ in license_todel:
                cur.execute("DELETE FROM license WHERE code == ?;", (license_,))
            con.commit()
            con.close()

            await message.channel.send("삭제 완료")

    if not isinstance(message.channel, discord.channel.DMChannel):
        if (message.author.guild_permissions.administrator or message.author.id in master_ids):
            if (message.content.startswith("!등록")):
                license_key = message.content.split(" ")[1]
                con = sqlite3.connect("../DB/" + "license.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
                search_result = cur.fetchone()
                con.close()
                if (search_result != None):
                    if (search_result[2] == 0):
                        if not (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                            con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                            cur = con.cursor()
                            cur.execute("CREATE TABLE serverinfo (id INTEGER, joinch INTEGER, expiredate TEXT, cultureid TEXT, culturepw TEXT, pw TEXT, roleid INTEGER, logwebhk TEXT, buylogwebhk TEXT, infoch INTEGER, chargech INTEGER, buych INTEGER, culture_fee INTEGER, bank TEXT);")
                            con.commit()
                            first_pw = randomstring.pick(10)
                            cur.execute("INSERT INTO serverinfo VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (message.guild.id, 0, make_expiretime(30), "", "", first_pw, 0, "", "", 0, 0, 0, 10, ""))
                            con.commit()
                            cur.execute("CREATE TABLE users (id INTEGER, money INTEGER, bought INTEGER);")
                            con.commit()
                            cur.execute("CREATE TABLE products (name INTEGER, money INTEGER, stock TEXT);")
                            con.commit()
                            con.close()
                            con = sqlite3.connect("../DB/" + "license.db")
                            cur = con.cursor()
                            cur.execute("UPDATE license SET isused = ?, useddate = ?, usedby = ? WHERE code == ?;", (1, nowstr(), message.guild.id, license_key))
                            con.commit()
                            con.close()
                            await message.channel.send(embed=embed("success", "서버 등록 성공", "서버가 성공적으로 등록되었습니다.\n라이센스 기간: `30`일\n만료일: `" + make_expiretime(30) + "`\n웹 패널:호스팅X/\n아이디: `" +str(message.guild.id) + "`\n비밀번호: `" + first_pw + "`"))
                        else:
                            await message.channel.send(embed=embed("warning", "서버 등록 실패", "이미 등록된 서버이므로 등록할 수 없습니다.\n기간 추가를 원하신다면 !라이센스 명령어를 이용해주세요."))
                    else:
                        await message.channel.send(embed=embed("error", "서버 등록 실패", "이미 사용된 라이센스입니다.\n관리자에게 문의해주세요."))
                else:
                    await message.channel.send(embed=embed("error", "서버 등록 실패", "존재하지 않는 라이센스입니다."))
            if message.content.startswith("!수동충전 "):
                try:
                    userId = message.mentions[0].id
                except:
                    userId = int(message.content.split(" ")[1])
                try:
                    amount = message.content.split(" ")[2]
                except:
                    return await message.channel.send(embed=embed("error", "수동 충전 실패", "`!수동충전 @유저멘션 충전금액` 으로 사용해주세요!"))
                
                con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE id == ?;", (userId,))
                user_info = cur.fetchone()
                if not user_info:
                    return await message.channel.send(embed=embed("error", "수동 충전 실패", f"가입하지 않은 유저입니다!\n<@{userId}> 님이 `!가입` 명령어를 통해 가입후 다시 시도하세요."))
                current_money = int(user_info[1])
                now_money = current_money + int(amount)
                cur.execute("UPDATE users SET money = ? WHERE id == ?;", (now_money, userId))
                con.commit()
                await message.channel.send(embed=embed("success", "수동 충전 성공", f"관리자: {message.author}\n기존 금액: `{current_money}`\n충전한 금액: `{amount}`\n충전 후 금액: `{now_money}`원").set_footer(text=message.guild.name))
                try:
                    webhook = DiscordWebhook(username="CrossVending Bot", avatar_url="https://cdn.discordapp.com/attachments/794207652602708019/794572711376453642/4460d42506dfee4b6f7796acc1c6d604.gif", url=get_logwebhk(message.guild.id))
                    eb = DiscordEmbed(title='수동 충전 성공', description='수동 충전 성공', color=0x00ff00)
                    eb.add_embed_field(name='관리자', value=f"{message.author}", inline=False)
                    eb.add_embed_field(name='디스코드 닉네임', value=f"<@{userId}>({message.mentions[0] if len(message.mentions) >= 1 else userId})", inline=False)
                    eb.add_embed_field(name='충전한 금액', value=f"`{amount}`원", inline=False)
                    webhook.add_embed(eb)
                    webhook.execute()
                except:
                    pass
                
    if not isinstance(message.channel, discord.channel.DMChannel):
        if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
            con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo;")
            cmdchs = cur.fetchone()
            con.close()
            try:
                tempvar = is_expired(cmdchs[2])
            except:
                os.rename("../DB/" + str(message.guild.id) + ".db", "../DB/" + str(message.guild.id) + f".db_old{datetime.datetime.now()}")
            if not(is_expired(cmdchs[2])):
                if (str(cmdchs[1]) == str(message.channel.id)):
                    if (message.content == "!가입"):
                        con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
                        user_info = cur.fetchone()
                        if (user_info == None):
                            cur.execute("INSERT INTO users VALUES(?, ?, ?);", (message.author.id, 0, 0))
                            con.commit()
                            await message.channel.send(embed=embed("success", "가입 성공", "성공적으로 가입되었습니다!\n!도움말 로 명령어 목록을 보세요."))
                        else:
                            await message.channel.send(embed=embed("error", "가입 실패", "이미 가입하셨습니다."))
                        con.close()

                if (str(cmdchs[9]) == str(message.channel.id)):
                    if (message.content == "!정보"):
                        con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
                        user_info = cur.fetchone()
                        con.close()
                        if (user_info != None):
                            try:
                                await message.author.send(embed=embed("primary", str(message.author.name) + "님의 정보", "유저 ID: `" + str(message.author.id) + "`\n보유 금액: `" + str(user_info[1]) + "`원\n누적 금액: `" + str(user_info[2]) + "`원").set_footer(text=message.guild.name))
                                await message.channel.send(embed=embed("success", "정보 조회 성공", "DM을 확인해주세요."))
                            except:
                                await message.channel.send(embed=embed("error", "정보 조회 실패", "DM을 차단하셨거나 메시지 전송 권한이 없습니다."))
                        else:
                            await message.channel.send(embed=embed("error", "정보 조회 실패", "먼저 가입해주세요."))

                if (str(cmdchs[10]) == str(message.channel.id)):
                    if (message.content.startswith("!계좌충전")):
                        con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM serverinfo")
                        serverinfo = cur.fetchone()
                        con.close()
                        try:
                            bankdata = json.loads(serverinfo[13])
                            assert len(bankdata['banknum']) > 1
                        except Exception as e:
                            return await message.channel.send(embed=embed("error", "계좌충전 불러오기 실패", "서버에 계좌정보가 등록되어있지 않습니다.\n샵 관리자에게 문의해주세요."))
                        try:
                            await message.author.send(embed=embed("primary", "계좌이체 충전", f"```{bankdata.get('bankname')} {bankdata.get('banknum')} {bankdata.get('bankowner')}```으로 충전을 원하는 금액을 아래 입금자명으로 입금해주세요.\n\n<@{message.author.id}>님의 고유 입금자명: `{str(hash(str(message.author.id)))[1:6]}`").set_footer(text=message.guild.name))
                            await message.channel.send(embed=embed("success", "충전 신청 완료", "DM을 확인해주세요."))
                        except Exception as e:
                            print(e)
                            return await message.channel.send(embed=embed("error", "계좌이체 충전 실패", "DM을 차단하셨거나 메시지 전송 권한이 없습니다."))
                        try:
                            webhook = DiscordWebhook(username="CrossVending Bot", avatar_url="https://cdn.discordapp.com/attachments/794207652602708019/794572711376453642/4460d42506dfee4b6f7796acc1c6d604.gif", url=get_logwebhk(message.guild.id))
                            eb = DiscordEmbed(title='계좌이체 충전 요청', description='[웹 패널로 이동하기](호스팅X)', color=0x00ffff)
                            eb.add_embed_field(name='디스코드 닉네임', value=f"<@{message.author.id}>({message.author})", inline=False)
                            eb.add_embed_field(name='입금자명', value=f"{str(hash(str(message.author.id)))[1:6]}", inline=False)
                            eb.add_embed_field(name='입금 확인후 충전방법', value=f"!수동충전 <@{message.author.id}> 받은금액", inline=False)
                            webhook.add_embed(eb)
                            webhook.execute()
                        except:
                            pass
                    if (message.content == "!충전"):
                        con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
                        user_info = cur.fetchone()
                        cur.execute("SELECT * FROM serverinfo;")
                        server_info = cur.fetchone()
                        con.close()
                        if (server_info[3] != "" and server_info[4] != ""):
                            if (user_info != None):
                                try:
                                    await message.author.send(embed=embed("primary", "문화상품권 충전 방법", "문화상품권 코드를 `-`을 포함해서 입력해주세요.").set_footer(text=message.guild.name))
                                    await message.channel.send(embed=embed("success", "충전 신청 완료", "DM을 확인해주세요."))
                                except:
                                    await message.channel.send(embed=embed("error", "문화상품권 충전 실패", "DM을 차단하셨거나 메시지 전송 권한이 없습니다."))
                                    return None

                                def check(msg):
                                    return (isinstance(msg.channel, discord.channel.DMChannel) and (len(msg.content) == 21 or len(msg.content) == 19) and (message.author.id == msg.author.id))
                                try:
                                    msg = await client.wait_for("message", timeout=60, check=check)
                                except asyncio.TimeoutError:
                                    try:
                                        await message.author.send(embed=embed("error", "문화상품권 충전 실패", "시간 초과되었습니다."))
                                    except:
                                        pass
                                    return None
                                
                                try:
                                    jsondata = {"token" : "토큰", "id" : server_info[3], "pw" : server_info[4], "pin" : msg.content}
                                    res = requests.post("API 주소", json=jsondata)
                                    if (res.status_code != 200):
                                        raise TypeError
                                    else:
                                        print(str(res))
                                        res = res.json()
                                except:
                                    try:
                                        await message.author.send(embed=embed("error", "문화상품권 충전 실패", "일시적인 서버 오류입니다.\n잠시 후 다시 시도해주세요."))
                                    except:
                                        pass
                                    return None

                                if (res["result"] == True):
                                    con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                                    cur = con.cursor()
                                    cur.execute("SELECT * FROM serverinfo WHERE id == ?;",(message.guild.id,))
                                    guild_info = cur.fetchone()
                                    culture_fee = int(guild_info[12])
                                    culture_amount = int(res["amount"])
                                    culture_amount_after_fee = culture_amount - int(culture_amount*(culture_fee/100))
                                    cur = con.cursor()
                                    cur.execute("SELECT * FROM users WHERE id == ?;", (msg.author.id,))
                                    user_info = cur.fetchone()
                                    current_money = int(user_info[1])
                                    now_money = current_money + culture_amount_after_fee
                                    cur.execute("UPDATE users SET money = ? WHERE id == ?;", (now_money, msg.author.id))
                                    con.commit()
                                    con.close()
                                    try:
                                        await message.author.send(embed=embed("success", "문화상품권 충전 성공", f"핀코드: `{msg.content}`\n금액: `{culture_amount}`원\n충전한 금액: `{culture_amount_after_fee}` (수수료 {culture_fee}%)\n충전 후 금액: `{now_money}`원").set_footer(text=message.guild.name))
                                        try:
                                            webhook = DiscordWebhook(username="CrossVending Bot", avatar_url="https://cdn.discordapp.com/attachments/794207652602708019/794572711376453642/4460d42506dfee4b6f7796acc1c6d604.gif", url=get_logwebhk(message.guild.id))
                                            eb = DiscordEmbed(title='문화상품권 충전 성공', description='[웹 패널로 이동하기](호스팅X)', color=0x00ff00)
                                            eb.add_embed_field(name='디스코드 닉네임', value=f"{msg.author}", inline=False)
                                            eb.add_embed_field(name='핀 코드', value=f"{msg.content}", inline=False)
                                            eb.add_embed_field(name='상품권 금액', value=f"`{culture_amount}`원", inline=False)
                                            eb.add_embed_field(name='충전한 금액', value=f"`{culture_amount_after_fee}`원 (수수료 {culture_fee}%)", inline=False)
                                            webhook.add_embed(eb)
                                            webhook.execute()
                                        except:
                                            pass
                                    except:
                                        pass
                                else:
                                    try:
                                        await message.author.send(embed=embed("error", "문화상품권 충전 실패", "[ " + res["reason"] + " ]"))
                                        try:
                                            webhook = DiscordWebhook(username="CrossVending Bot", avatar_url="https://cdn.discordapp.com/attachments/794207652602708019/794572711376453642/4460d42506dfee4b6f7796acc1c6d604.gif", url=get_logwebhk(message.guild.id))
                                            eb = DiscordEmbed(title='문화상품권 충전 실패', description='[웹 패널로 이동하기](호스팅X)', color=0xff0000)
                                            eb.add_embed_field(name='디스코드 닉네임', value=str(msg.author), inline=False)
                                            eb.add_embed_field(name='핀 코드', value=str(msg.content), inline=False)
                                            eb.add_embed_field(name='실패 사유', value=res["reason"], inline=False)
                                            webhook.add_embed(eb)
                                            webhook.execute()
                                        except Exception as e:
                                            await message.author.send(e)
                                    except:
                                        pass
                            
                            else:
                                await message.channel.send(embed=embed("error", "문화상품권 충전 실패", "먼저 가입해주세요."))
                        else:
                            await message.channel.send(embed=embed("error", "문화상품권 충전 실패", "충전 기능이 비활성화되어 있습니다.\n샵 관리자에게 문의해주세요."))
                
                if (str(cmdchs[11]) == str(message.channel.id)):
                    if (message.content.startswith("!구매 ")):
                        product_name = message.content.split(" ")[1:]
                        product_name = " ".join(product_name)
                        con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
                        user_info = cur.fetchone()
                        cur.execute("SELECT * FROM products WHERE name == ?;", (product_name,))
                        product_info = cur.fetchone()
                        con.close()
                        if (user_info != None):
                            if (product_info != None):
                                if (str(product_info[2]) != ""):
                                    info_msg = await message.channel.send(embed=embed("warning", "수량 선택", "구매하실 수량을 숫자만 입력해주세요."))
                                    def check(msg):
                                        return (msg.author.id == message.author.id)
                                    try:
                                        msg = await client.wait_for("message", timeout=20, check=check)
                                    except asyncio.TimeoutError:
                                        try:
                                            await info_msg.delete()
                                        except:
                                            pass
                                        await message.channel.send(embed=embed("error", "시간 초과", "처음부터 다시 시도해주세요."))
                                        return None

                                    try:
                                        await info_msg.delete()
                                    except:
                                        pass
                                    try:
                                        await msg.delete()
                                    except:
                                        pass

                                    if not ((msg.content.isdigit()) and (msg.content != "0") and (msg.content != "00") and (msg.content != "000") and (msg.content != "0000") and (msg.content != "00000") and (msg.content != "000000") and (msg.content != "0000000") and (msg.content != "00000000") and (msg.content != "000000000") and (msg.content != "0000000000") and (msg.content != "00000000000") and (msg.content != "000000000000") and (msg.content != "0000000000000")):
                                        await message.channel.send(embed=embed("error", "구매 실패", "수량은 숫자로만 입력해주세요."))
                                        return None

                                    buy_amount = int(msg.content)

                                    if (len(product_info[2].split("\n")) >= buy_amount):
                                        if (int(user_info[1]) >= int(product_info[1] * buy_amount)):
                                            try_msg = await message.channel.send(embed=embed("loading", "구매 진행 중입니다..", ""))
                                            stocks = product_info[2].split("\n")
                                            bought_stock = []
                                            for n in range(buy_amount):
                                                picked = random.choice(stocks)
                                                bought_stock.append(picked)
                                                stocks.remove(picked)
                                            now_stock = "\n".join(stocks)
                                            now_money = int(user_info[1]) - (int(product_info[1]) * buy_amount)
                                            now_bought = int(user_info[2]) + (int(product_info[1]) * buy_amount)
                                            con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                                            cur = con.cursor()
                                            cur.execute("UPDATE users SET money = ?, bought = ? WHERE id == ?;", (now_money, now_bought, message.author.id))
                                            con.commit()
                                            cur.execute("UPDATE products SET stock = ? WHERE name == ?;", (now_stock, product_name))
                                            con.commit()
                                            con.close()
                                            bought_stock = "\n".join(bought_stock)
                                            if (len(bought_stock) > 1000):
                                                con = sqlite3.connect("../DB/docs.db")
                                                cur = con.cursor()
                                                docs_name = randomstring.pick(30)
                                                cur.execute("INSERT INTO docs VALUES(?, ?);", (docs_name, bought_stock))
                                                con.commit()
                                                con.close()
                                                docs_url = "https://crossvending.kro.kr/rawviewer/" + docs_name
                                                try:
                                                    try:
                                                        webhook = DiscordWebhook(username="CrossVending Bot", avatar_url="https://cdn.discordapp.com/attachments/794207652602708019/794572711376453642/4460d42506dfee4b6f7796acc1c6d604.gif", url=get_logwebhk(message.guild.id))
                                                        eb = DiscordEmbed(title='제품 구매 로그', description='[웹 패널로 이동하기](호스팅X)', color=0x00ff00)
                                                        eb.add_embed_field(name='디스코드 닉네임', value=str(message.author), inline=False)
                                                        eb.add_embed_field(name='구매 제품', value=str(product_name), inline=False)
                                                        eb.add_embed_field(name='구매 코드', value='[구매한 코드 보기](' + docs_url + ')', inline=False)
                                                        webhook.add_embed(eb)
                                                        webhook.execute()
                                                    except:
                                                        pass

                                                    try:
                                                        webhook = DiscordWebhook(username="CrossVending Bot", avatar_url="https://cdn.discordapp.com/attachments/794207652602708019/794572711376453642/4460d42506dfee4b6f7796acc1c6d604.gif", url=get_buylogwebhk(message.guild.id))
                                                        webhook.add_embed(DiscordEmbed(description="<@" + str(message.author.id) + ">" + "님, `" + product_name + "` 제품 `" + str(buy_amount) + "`개 구매 감사합니다! :thumbsup:"))
                                                        webhook.execute()
                                                    except:
                                                        pass

                                                    try:
                                                        buyer_role = message.guild.get_role(get_roleid(message.guild.id))
                                                        await message.author.add_roles(buyer_role)
                                                    except:
                                                        pass

                                                    await message.author.send(embed=embed("success", "구매가 완료되었습니다!", "").add_field(name="구매하신 제품", value="`" + product_name + "`", inline=False).add_field(name="구매하신 코드", value='[구매한 코드 보기](' + docs_url + ')', inline=False).add_field(name="차감 금액", value="`" + str(int(product_info[1]) * buy_amount) + "`원", inline=False).set_footer(text=message.guild.name))
                                                    await try_msg.edit(embed=embed("success", "구매가 완료되었습니다!", "DM을 확인해주세요."))
                                                except:
                                                    try:
                                                        await try_msg.delete()
                                                    except:
                                                        await message.channel.send(embed=embed("error", "제품 구매 실패", "제품 구매 중 알 수 없는 오류가 발생했습니다.\n샵 관리자에게 문의해주세요."))

                                            else:
                                                try:
                                                    try:
                                                        webhook = DiscordWebhook(username="CrossVending Bot", avatar_url="https://cdn.discordapp.com/attachments/794207652602708019/794572711376453642/4460d42506dfee4b6f7796acc1c6d604.gif", url=get_logwebhk(message.guild.id))
                                                        eb = DiscordEmbed(title='제품 구매 로그', description='[웹 패널로 이동하기](호스팅X)', color=0x00ff00)
                                                        eb.add_embed_field(name='디스코드 닉네임', value=str(message.author), inline=False)
                                                        eb.add_embed_field(name='구매 제품', value=str(product_name), inline=False)
                                                        eb.add_embed_field(name='구매 코드', value=bought_stock, inline=False)
                                                        webhook.add_embed(eb)
                                                        webhook.execute()
                                                    except:
                                                        pass

                                                    try:
                                                        webhook = DiscordWebhook(username="CrossVending Bot", avatar_url="https://cdn.discordapp.com/attachments/794207652602708019/794572711376453642/4460d42506dfee4b6f7796acc1c6d604.gif", url=get_buylogwebhk(message.guild.id))
                                                        webhook.add_embed(DiscordEmbed(description="<@" + str(message.author.id) + ">" + "님, `" + product_name + "` 제품 `" + str(buy_amount) + "`개 구매 감사합니다! :thumbsup:"))
                                                        webhook.execute()
                                                    except:
                                                        pass

                                                    try:
                                                        buyer_role = message.guild.get_role(get_roleid(message.guild.id))
                                                        await message.author.add_roles(buyer_role)
                                                    except:
                                                        pass

                                                    await message.author.send(embed=embed("success", "구매가 완료되었습니다!", "").add_field(name="구매하신 제품", value="`" + product_name + "`", inline=False).add_field(name="구매하신 코드", value="`" + str(bought_stock) + "`", inline=False).add_field(name="차감 금액", value="`" + str(int(product_info[1]) * buy_amount) + "`원", inline=False).set_footer(text=message.guild.name))
                                                    await try_msg.edit(embed=embed("success", "구매가 완료되었습니다!", "DM을 확인해주세요."))
                                                except:
                                                    try:
                                                        await try_msg.delete()
                                                    except:
                                                        pass
                                                    await message.channel.send(embed=embed("error", "제품 구매 실패", "제품 구매 중 알 수 없는 오류가 발생했습니다.\n샵 관리자에게 문의해주세요."))
                                        else:
                                            await message.channel.send(embed=embed("error", "제품 구매 실패", "잔액이 부족합니다."))
                                    else:
                                        await message.channel.send(embed=embed("error", "제품 구매 실패", "재고가 부족합니다."))
                                else:
                                    await message.channel.send(embed=embed("error", "제품 구매 실패", "재고가 부족합니다."))
                            else:
                                await message.channel.send(embed=embed("error", "제품 구매 실패", "존재하지 않는 제품입니다."))
                        else:
                            await message.channel.send(embed=embed("error", "제품 구매 실패", "먼저 가입해주세요."))

                if (message.content == "!제품목록"):
                    con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products;")
                    products = cur.fetchall()
                    con.close()
                    list_embed = embed("primary", "제품 목록", "")
                    for product in products:
                        if (product[2] != ""):
                            list_embed.add_field(name=product[0], value="가격: `" + str(product[1]) + "`원\n재고: `" + str(len(product[2].split("\n"))) + "`개")
                        else:
                            list_embed.add_field(name=product[0], value="가격: " + str(product[1]) + "원\n재고: `0`개")

                    await message.channel.send(embed=list_embed)

                if (message.content == "!도움말"):
                    try:
                        await message.author.send(embed=embed("success", "CrossVending Bot 도움말", "```\n!가입 : 자판기에 가입합니다.\n!정보 : 자신의 정보를 조회합니다.\n!충전 : 문화상품권 충전을 진행합니다.\n!계좌충전 : 계좌이체 충전을 진행합니다.\n!구매 제품명 : 입력한 제품을 구매합니다.\n!제품목록 : 제품 목록, 가격, 재고 상황을 봅니다.```"))
                        await message.channel.send(embed=embed("success", "DM을 확인해주세요.", ""))
                    except:
                        await message.channel.send(embed=embed("error", "오류 발생", "도움말을 보낼 수 없습니다."))
    if message.content == '!서버수':
      servers = len(client.guilds)
      await message.channel.send(f"현재 CrossVending 봇은 {servers} 개의 서버에서 작동중입니다.")

    if message.content == '!유저수':
       await message.channel.send(f"{user_count}명의 유저분이 사용중")


client.run(token)