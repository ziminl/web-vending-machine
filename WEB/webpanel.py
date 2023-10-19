from flask import Flask, render_template, request, make_response
from flask import session, redirect, url_for, abort
from datetime import timedelta
import datetime
import time
import sqlite3
import randomstring
import os
import datetime
from datetime import timedelta
import ssl
import json

app = Flask(__name__)

app.secret_key = randomstring.pick(30)

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
        return str(round(days)) + "일 " + str(round(hours)) + "시간" 
    else:
        return False

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

@app.route("/", methods=["GET"])
def index():
    if ("id" in session):
        return redirect(url_for("login"))
    else:
        return redirect(url_for("setting"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method == "GET"):
        if ("id" in session):
            return redirect(url_for("setting"))
        else:
            return render_template("login.html")
    else:
        if ("id" in request.form and "pw" in request.form):
            if (request.form["id"].isdigit() and os.path.isfile("../DB/" + request.form["id"] + ".db")):
                con = sqlite3.connect("../DB/" + request.form["id"] + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM serverinfo")
                serverinfo = cur.fetchone()
                con.close()
                if (request.form["pw"] == serverinfo[5]):
                    session.clear()
                    session["id"] = request.form["id"]
                    return """<script>alert("로그인에 성공했습니다!"); window.location.href = "/setting";</script>"""
                else:
                    return """<script>alert("비밀번호가 틀렸습니다."); window.location.href = "/login";</script>"""
            else:
                return """<script>alert("아이디가 틀렸습니다."); window.location.href = "/login";</script>"""
        else:
            return """<script>alert("아이디가 틀렸습니다."); window.location.href = "/login";</script>"""

@app.route("/setting", methods=["GET", "POST"])
def setting():
    if (request.method == "GET"):
        if ("id" in session):
            con = sqlite3.connect("../DB/" + session["id"] + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo")
            serverinfo = cur.fetchone()
            con.close()
            try:
                bank = json.loads(serverinfo[13])
                bank['banknum']
            except:
                bank = {}
            return render_template("manage.html", info=serverinfo, bank=bank)
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if (session["id"] != "423045193902850049"):
                if ("cultureid" in request.form and "culturepw" in request.form and "joinch" in request.form and "logwebhk" in request.form and "buylogwebhk" in request.form and "roleid" in request.form and "infoch" in request.form and "chargech" in request.form and "buych" in request.form):
                    if (request.form["joinch"].isdigit() and request.form["infoch"].isdigit() and request.form["chargech"].isdigit() and request.form["buych"].isdigit() and request.form['fee'].isdigit()):
                        if (request.form["roleid"].isdigit()):
                            con = sqlite3.connect("../DB/" + session["id"] + ".db")
                            cur = con.cursor()
                            bankdata={"bankname": request.form['bankname'],"banknum": request.form['banknum'],"bankowner": request.form['bankowner']}
                            cur.execute("UPDATE serverinfo SET cultureid = ?, culturepw = ?, joinch = ?, logwebhk = ?, buylogwebhk = ?, roleid = ?, infoch = ?, chargech = ?, buych = ?, culture_fee = ?, bank = ?;", (request.form["cultureid"], request.form["culturepw"], request.form["joinch"], request.form["logwebhk"], request.form["buylogwebhk"], request.form["roleid"], request.form["infoch"], request.form["chargech"], request.form["buych"], request.form['fee'], json.dumps(bankdata)))
                            con.commit()
                            con.close()
                            return "ok"
                        else:
                            return "역할 ID는 숫자로만 입력해주세요."
                    else:
                        return "명령어 채널 ID는 숫자로만 입력해주세요."
                else:
                    return "잘못된 접근입니다."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/manageuser", methods=["GET"])  
def manageuser():
    if ("id" in session):
        con = sqlite3.connect("../DB/" + session["id"] + ".db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        con.close()
        return render_template("manage_user.html", users=users)
    else:
        return redirect(url_for("login"))

@app.route("/manageuser_detail", methods=["GET", "POST"])  
def manageuser_detail():
    if (request.method == "GET"):
        if ("id" in session):
            user_id = request.args.get("id", "")
            if (user_id != ""):
                con = sqlite3.connect("../DB/" + session["id"] + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
                user_info = cur.fetchone()
                con.close()
                if (user_info != None):
                    return render_template("manage_user_detail.html", info=user_info)
                else:
                    abort(404)
            else:
                abort(404)
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("money" in request.form and "bought" in request.form and "id" in request.form):
                if (request.form["money"].isdigit()):
                    if (request.form["bought"].isdigit()):
                        con = sqlite3.connect("../DB/" + session["id"] + ".db")
                        cur = con.cursor()
                        cur.execute("UPDATE users SET money = ?, bought = ? WHERE id == ?;", (request.form["money"], request.form["bought"], request.form["id"]))
                        con.commit()
                        con.close()
                        return "ok"
                    else:
                        return "누적 금액은 정수로만 적어주세요."
                else:
                    return "잔액은 정수로만 적어주세요."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/manageprod", methods=["GET"])  
def manageprod():
    if ("id" in session):
        con = sqlite3.connect("../DB/" + session["id"] + ".db")
        cur = con.cursor()
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        con.close()
        return render_template("manage_prod.html", products=products)
    else:
        return redirect(url_for("login"))

@app.route("/delete_product", methods=["POST"])  
def deleteprod():
    if ("id" in session):
        if ("name" in request.form):
            con = sqlite3.connect("../DB/" + session["id"] + ".db")
            cur = con.cursor()
            cur.execute("DELETE FROM products WHERE name == ?;", (request.form["name"],))
            con.commit()
            con.close()
            return "ok"
        else:
            return "fail"
    else:
        return "fail"

@app.route("/manageprod_detail", methods=["GET", "POST"])
def manageprod_detail():
    if (request.method == "GET"):
        if ("id" in session):
            product_name = request.args.get("id", "")
            if (product_name != ""):
                con = sqlite3.connect("../DB/" + session["id"] + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM products WHERE name == ?;", (product_name,))
                prod_info = cur.fetchone()
                con.close()
                if (prod_info != None):
                    return render_template("manage_prod_detail.html", info=prod_info)
                else:
                    abort(404)
            else:
                abort(404)
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("price" in request.form and "stock" in request.form and "name" in request.form):
                if (request.form["price"].isdigit()):
                    con = sqlite3.connect("../DB/" + session["id"] + ".db")
                    cur = con.cursor()
                    cur.execute("UPDATE products SET money = ?, stock = ? WHERE name == ?;", (request.form["price"], request.form["stock"], request.form["name"]))
                    con.commit()
                    con.close()
                    return "ok"
                else:
                    return "가격은 숫자로만 적어주세요."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/createprod", methods=["GET", "POST"])
def createprod():
    if (request.method == "GET"):
        if ("id" in session):
            return render_template("create_prod.html")
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("price" in request.form and "name" in request.form):
                if (request.form["price"].isdigit()):
                    con = sqlite3.connect("../DB/" + session["id"] + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products WHERE name == ?;", (request.form["name"],))
                    prod = cur.fetchone()
                    if (prod == None):
                        con = sqlite3.connect("../DB/" + session["id"] + ".db")
                        cur = con.cursor()
                        cur.execute("INSERT INTO products VALUES(?, ?, ?);", (request.form["name"], request.form["price"], ""))
                        con.commit()
                        con.close()
                        return "ok"
                    else:
                        return "이미 존재하는 제품명입니다."
                else:
                    return "가격은 숫자로만 적어주세요."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/license", methods=["GET", "POST"])
def managelicense():
    if (request.method == "GET"):
        if ("id" in session):
            con = sqlite3.connect("../DB/" + session["id"] + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo")
            serverinfo = cur.fetchone()
            con.close()
            if (is_expired(serverinfo[2])):
                return render_template("manage_license.html", expire="0일 0시간 (만료됨)")
            else:
                return render_template("manage_license.html", expire=get_expiretime(serverinfo[2]))
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("code" in request.form):
                license_key = request.form["code"]
                con = sqlite3.connect("../DB/" + "license.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
                search_result = cur.fetchone()
                con.close()
                if (search_result != None):
                    if (search_result[2] == 0):
                        con = sqlite3.connect("../DB/" + "license.db")
                        cur = con.cursor()
                        cur.execute("UPDATE license SET isused = ?, useddate = ?, usedby = ? WHERE code == ?;", (1, nowstr(), session["id"], license_key))
                        con.commit()
                        cur = con.cursor()
                        cur.execute("SELECT * FROM license WHERE code == ?;",(license_key,))
                        key_info = cur.fetchone()
                        con.close()
                        con = sqlite3.connect("../DB/" + session["id"] + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM serverinfo;")
                        server_info = cur.fetchone()
                        if (is_expired(server_info[2])):
                            new_expiretime = make_expiretime(key_info[1])
                        else:
                            new_expiretime = add_time(server_info[2], key_info[1])
                        cur.execute("UPDATE serverinfo SET expiredate = ?;", (new_expiretime,))
                        con.commit()
                        con.close()
                        return f"{key_info[1]}"
                    else:
                        return "이미 사용된 라이센스입니다."
                else:
                    return "존재하지 않는 라이센스입니다."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/rawviewer/<docsid>", methods=["GET"])
def rawviewer(docsid):
    con = sqlite3.connect("../DB/docs.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM docs WHERE id == ?;", (docsid,))
    docs_info = cur.fetchone()
    con.close()
    if (docs_info != None):
        return docs_info[1].replace("\n", "<br>")
    else:
        return "알 수 없는 문서 ID입니다."
    
@app.route("/logout", methods=["GET"])
def logout():
    session.clear() 
    return redirect(url_for("login"))

@app.before_request 
def make_session_permanent(): 
    session.permanent = True 
    app.permanent_session_lifetime = timedelta(minutes=60) 

@app.errorhandler(404)
def not_found_error(error):
  return render_template("404.html")

if __name__ == '__main__':
    app.run(host='118.220.186.75', port=8080) #보안 호스트 