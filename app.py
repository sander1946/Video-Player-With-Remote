import base64
import hashlib
import random
import json
import requests
import bcrypt
import pymysql.cursors
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, session, g
from hashids import Hashids

app = Flask(__name__)
app.config["SECRET_KEY"] = "438324438324438324"
app.secret_key = app.config["SECRET_KEY"]
hashids = Hashids(min_length=6, salt=app.config["SECRET_KEY"])

databases = {
    "login": "login - studentsander.nl",
    "data": "data - studentsander.nl",
}


def get_ip_location(ip: str):
    print(ip)
    if ip != "0.0.0.0":
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0'}
        api = f"http://api.ipstack.com/{ip}?access_key=31723cb5317b6589212b8d1a30aeef66"
        response = requests.get(api, headers=headers)
        print(response)
        if response.status_code == 200:
            ip_information = json.loads(response.content.decode('utf-8'))
            print(ip_information)
            for x in ip_information:
                if ip_information[x] is not None:
                    if x == "location":
                        for y in ip_information[x]:
                            if ip_information[x][y] is not None:
                                if y == "languages":
                                    for z in ip_information[x][y][0]:
                                        if ip_information[x][y] is not None:
                                            session[z] = ip_information[x][y][0][z]
                            else:
                                session[y] = ip_information[x][y]
                else:
                    session[x] = ip_information[x]


def connect_to_database(name: str, data_bases: dict):
    try:
        connection = pymysql.connect(host='127.0.0.1',
                                     user='sande',
                                     password='43832Magie43832',
                                     database=data_bases[name],
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection
    except pymysql.err as error:
        print(f"Error while connecting to MySQL database: {error}")
    finally:
        print(f"Connection to '{data_bases[name]}' was successful")
        pass


def prep_password(password: str) -> bytes:
    byte = password.encode("utf-8")
    sha256 = hashlib.sha256(byte).digest()
    base = base64.b64encode(sha256)
    return base


def ip_logger() -> str:
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent")
    hostname = request.host
    referrer = request.referrer
    return ip_address, user_agent, hostname, referrer


@app.before_request
def before_request():
    g.user = None
    if "user_id" in session:
        g.user = session["user_id"]


@app.route("/drop_session")
def drop_session():
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/", methods=("GET", "POST"))
def main_page():
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/facebook", methods=("GET", "POST"))
def facebook_page():
    return render_template("facebook.html")


@app.route("/login", methods=('GET', 'POST'))
def login_page():
    if request.method == "POST":
        session.pop("user_id", None)
        connection = connect_to_database("login", databases)
        if "email" in request.form and "password" in request.form:
            email = request.form["email"]
            password = request.form["password"]
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM `login_data` WHERE `email` = %s",
                                   [email])
                    login_info = cursor.fetchone()
                    user_id = login_info["id"]
                    user_name = login_info["name"]
                    user_email = login_info["email"]
                    hashed_password = str(login_info["password"]).encode()
                    if login_info is not None:
                        prepared_password = prep_password(password)
                        if bcrypt.checkpw(prepared_password, hashed_password):
                            session["user_id"] = user_id
                            session["user_name"] = user_name
                            session["user_email"] = user_email
                            connection.commit()
                            return redirect(url_for("profile_page"))
                        else:
                            connection.commit()
                            return redirect(url_for("login_page"))
                    else:
                        connection.commit()
                        return redirect(url_for("login_page"))
    return render_template("login.html")


@app.route("/register", methods=('GET', 'POST'))
def register_page():
    if request.method == "POST":
        connection = connect_to_database("login", databases)
        if "name" in request.form and "email" in request.form and "password" in request.form:
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT `email` FROM `login_data` WHERE `email` = %s",
                                   [email])
                    user_data = cursor.fetchone()
                    if user_data is not None:
                        if user_data["email"] == email:
                            connection.commit()
                            return redirect(url_for("login_page"))
                    else:
                        password_salt = bcrypt.gensalt()
                        prepared_password = prep_password(password)
                        hashed_password = bcrypt.hashpw(prepared_password, password_salt)
                        cursor.execute("INSERT INTO `login_data` (`name`, `email`, `password`) VALUES (%s, %s, %s)",
                                       [name, email, hashed_password])
                        connection.commit()
                        return redirect(url_for("profile_page"))
    return render_template("register.html")


@app.route("/profile", methods=('GET', 'POST'))
def profile_page():
    if g.user:
        if request.method == "POST":
            if "logout" in request.form:
                # user set and loging out
                return redirect(url_for("drop_session"))
            else:
                # user set and did not click logout
                return render_template("profile.html")
        else:
            # user set and did not click logout
            return render_template("profile.html", name=session["user_name"], email=session["user_email"])
    else:
        # user not set
        return redirect(url_for("login_page"))


@app.route("/url", methods=("GET", "POST"))
def track_url():
    if g.user:
        connection = connect_to_database("data", databases)
        if request.method == "POST":
            url = request.form["url"]

            if not url:
                flash("The URL is required!")
                return redirect(url_for("track_url"))

            temp_id = random.randint(0, 1000000000)
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO `url_data` (`original_url`, `url_id`, `made_by`) VALUES (%s, %s, %s)",
                                   [url, temp_id, session["user_id"]])
                    url_id = cursor.lastrowid
                    # print(url_id)
                    hashid = hashids.encode(url_id)
                    track = "link/"
                    view = "view/"
                    display_view_url = request.host_url + view + hashid
                    display_track_url = request.host_url + track + hashid
                    cursor.execute("UPDATE `url_data` SET `url_id` = %s WHERE `url_id` = %s",
                                   [hashid, temp_id])
                    cursor.execute("INSERT INTO `ip_data` (`url_id`, `mail_id`, `made_by`) VALUES (%s, %s, %s)",
                                   [hashid, "NULL", session["user_id"]])
                    connection.commit()
                # connection.close()
            return render_template("URL.html", display_track_url=display_track_url,
                                   display_view_url=display_view_url)
        return render_template("URL.html")
    return redirect(url_for("login_page"))


@app.route("/link/<link_id>", methods=('GET', 'POST'))
def url_redirect(link_id):
    connection = connect_to_database("data", databases)
    original_id = hashids.decode(link_id)
    if original_id:
        original_id = original_id[0]
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT original_url, clicks FROM url_data WHERE id = %s",
                               [str(original_id)])
                url_data = cursor.fetchone()
                original_url = url_data["original_url"]
                clicks = url_data["clicks"]
                ip_address, user_agent, hostname, referrer = ip_logger()

                cursor.execute("UPDATE `url_data` SET `clicks` = %s WHERE `id` = %s",
                               [clicks + 1, str(original_id)])
                cursor.execute("UPDATE `ip_data` SET `ip` = %s, `hostname` = %s, `referrer` = %s, `user_agent` = %s"
                               "WHERE `url_id` = %s",
                               [ip_address, hostname, referrer, user_agent, str(link_id)])
            connection.commit()
        # connection.close()
        return redirect(f"https://{original_url}")
    else:
        flash("Invalid URL!")
        return redirect(url_for("track_url"))


@app.route("/view/<link_id>", methods=('GET', 'POST'))
def view_click_data(link_id):
    connection = connect_to_database("data", databases)
    original_id = hashids.decode(link_id)
    if original_id:
        original_id = original_id[0]
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT original_url, clicks, created FROM url_data "
                               "WHERE id = %s", [str(original_id)])
                url_data = cursor.fetchone()
                cursor.execute("SELECT ip, hostname, referrer, user_agent FROM ip_data WHERE url_id = %s",
                               [str(link_id)])
                ip_data = cursor.fetchone()
                original_url = url_data["original_url"]
                clicks = url_data["clicks"]
                created = url_data["created"]
                ip = ip_data["ip"]
                hostname = ip_data["hostname"]
                referrer = ip_data["referrer"]
                agent = ip_data["user_agent"]
                get_ip_location(ip)
            connection.commit()
        # connection.close()
        return render_template("view_clicks.html", original_url=original_url, clicks=clicks,
                               ip=ip, hostname=hostname, referrer=referrer, agent=agent,
                               created=created, link_id=link_id, session_info=session)
    else:
        flash("Invalid URL!")
        return redirect(url_for("track_url"))


@app.route("/mail", methods=("GET", "POST"))
def mail_tracker():
    if g.user:
        print(g.user)
        connection = connect_to_database("data", databases)
        if request.method == "POST":
            mail_address = request.form["mail_address"]

            if not mail_address:
                flash("The email address is required!")
                return redirect(url_for("mail_tracker"))
            with connection:
                with connection.cursor() as cursor:
                    temp_id = random.randint(0, 1000000000)
                    cursor.execute("INSERT INTO `mail_data` (`mail_address`, `mail_id`, `made_by`) VALUES (%s, %s, %s)",
                                   [mail_address, temp_id, session["user_id"]])
                    url_id = cursor.lastrowid
                    hashid = hashids.encode(url_id)
                    extension = ".png"
                    track = "images/"
                    view = "site/"
                    display_image = request.host_url + track + hashid + extension
                    display_view_mail_status = request.host_url + view + hashid + extension
                    cursor.execute("UPDATE `mail_data` SET `mail_id` = %s WHERE `mail_id` = %s",
                                   [(hashid + extension), temp_id])
                    cursor.execute("INSERT INTO `ip_data` (`mail_id`, `url_id`, `made_by`) VALUES (%s, %s, %s)",
                                   [(hashid + extension), "NULL", session["user_id"]])
                connection.commit()
            # connection.close()
            return render_template("MAIL.html", display_view_mail_status=display_view_mail_status,
                                   display_image=display_image)
        return render_template("MAIL.html")
    return redirect(url_for("login_page"))


@app.route("/images/<file>", methods=('GET', 'POST'))
def view_image_file(file):
    connection = connect_to_database("data", databases)
    original_file_id = str(file[0:-4])
    original_id = hashids.decode(original_file_id)
    if original_id:
        original_id = original_id[0]
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT `times_opened` FROM `mail_data` WHERE `id` = %s",
                               [str(original_id)])
                url_data = cursor.fetchone()
                times_opened = url_data["times_opened"]
                ip_address, user_agent, hostname, referrer = ip_logger()
                cursor.execute("UPDATE `mail_data` SET `times_opened` = %s WHERE `id` = %s",
                               [times_opened + 1, str(original_id)])
                cursor.execute("UPDATE `ip_data` SET `ip` = %s, `hostname` = %s, `referrer` = %s, `user_agent` = %s"
                               "WHERE `mail_id` = %s",
                               [ip_address, hostname, referrer, user_agent, str(file)])
            connection.commit()
        # connection.close()
    return send_from_directory("P:/sites/studentsander.nl/assets/imgs", "1x1.png")


@app.route("/site/<file>", methods=('GET', 'POST'))
def view_mail_data(file):
    connection = connect_to_database("data", databases)
    short_file_id = str(file[0:-4])
    original_id = hashids.decode(short_file_id)
    if original_id:
        original_id = original_id[0]
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT `mail_address`, `times_opened` FROM `mail_data` "
                               "WHERE `id` = %s",
                               [str(original_id)])
                click_data = cursor.fetchone()
                cursor.execute("SELECT ip, hostname, referrer, user_agent FROM ip_data WHERE mail_id = %s",
                               [str(file)])
                ip_data = cursor.fetchone()
                mail_address = click_data["mail_address"]
                times_opened = click_data["times_opened"]
                ip = ip_data["ip"]
                hostname = ip_data["hostname"]
                referrer = ip_data["referrer"]
                agent = ip_data["user_agent"]
                connection.commit()
        # connection.close()
        return render_template("view_opened_mail.html", mail_address=mail_address,
                               ip=ip, hostname=hostname, referrer=referrer, agent=agent,
                               times_opened=times_opened, file=file)
    else:
        flash("Invalid URL!")
        return redirect(url_for("mail_tracker"))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
