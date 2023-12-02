import random
import json
import requests
import pymysql.cursors
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, session, g

app = Flask(__name__)


def connect_to_database():
    try:
        connection = pymysql.connect(host='192.168.2.170',
                                     user='Hubo',
                                     password='Hubo2015',
                                     database="videos",
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection
    except pymysql.err as error:
        print(f"Error while connecting to MySQL database: {error}")
    finally:
        print(f"Connection to the database was successful")
        pass


@app.route("/", methods=("GET", "POST"))
def main_page():
    session.clear()
    return redirect(url_for("login_page"))


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
            connection.commit()
        # connection.close()
        return render_template("view_clicks.html", original_url=original_url, clicks=clicks,
                               ip=ip, hostname=hostname, referrer=referrer, agent=agent,
                               created=created, link_id=link_id, session_info=session)
    else:
        flash("Invalid URL!")
        return redirect(url_for("track_url"))


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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
