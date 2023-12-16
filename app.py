from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import pymysql.cursors
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "438324438324438324"
app.secret_key = app.config["SECRET_KEY"]


def read_global_code():
    f = open("code.txt", 'r')
    glob_code = f.read()
    f.close()
    f = open("pref_code.txt", 'r')
    pref_code = f.read()
    f.close()
    f = open("loop_id.txt", 'r')
    loop_id = f.read()
    f.close()
    return glob_code, pref_code, loop_id


def write_global_code(glob_code):
    f = open("code.txt", 'w')
    print(glob_code)
    f.write(glob_code)
    f.close()


def write_pref_code(pref_code):
    f = open("pref_code.txt", 'w')
    print(pref_code)
    f.write(pref_code)
    f.close()


def write_loop_id(loop_id):
    f = open("loop_id.txt", 'w')
    print(loop_id)
    f.write(loop_id)
    f.close()


def connect_to_database():
    connection = pymysql.connect(host='192.168.2.17',
                                 user='Hubo',
                                 password='Hubo2015',
                                 database="videos",
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


@app.before_request
def before_request():
    if "code" in session:
        write_global_code(session["code"])


@app.route("/send_code", methods=["POST"])
def send_code():
    json_data = json.loads(request.data)
    code = json_data["code"]
    write_global_code(str(code))
    return {"data": "test"}


@app.route("/drop")
def drop_session():
    session.clear()
    write_global_code(str(0))
    return redirect(url_for("index"))


@app.route('/_get_video', methods=['GET'])
def get_video():
    code, pref_code, loop_id = read_global_code()
    if code != 0:
        connection = connect_to_database()
        with connection:
            with connection.cursor() as cursor:
                if code == pref_code:
                    is_new = False
                    if int(loop_id) >= 80:
                        loop_id = 0
                        write_loop_id(str(loop_id))
                    loop_id = int(loop_id) + 1
                    cursor.execute("SELECT * FROM `videos` WHERE `id` = %s",
                                   [loop_id])
                else:
                    is_new = True
                    write_pref_code(str(code))
                    cursor.execute("SELECT * FROM `videos` WHERE `code` = %s",
                                   [code])
                vuurwerk_info = cursor.fetchone()
                vid = vuurwerk_info["vid"]
                start = vuurwerk_info["start"]
                duration = vuurwerk_info["duration"]
        return jsonify(video=f"https://www.youtube-nocookie.com/embed/{vid}&start={start}&autoplay=1&mute=1",
                       duration=duration, is_new=is_new)
    return jsonify(video="None", duration=2500)


@app.route('/player', methods=('GET', 'POST'))
def player():
    return render_template('Video_Player.html')


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.args.get("code") is not None:
        code = request.args.get("code")
        write_global_code(code)
    return render_template('Video_Selecter.html')


@app.route('/_get_list', methods=['GET'])
def get_list():
    connection = connect_to_database()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM `videos`")
            list_info = cursor.fetchall()
            new_list_info = []
            for x in list_info:
                a = []
                counter = 0
                for y in x:
                    if counter != 0:
                        a.append(x[y])
                    counter += 1
                new_list_info.append(a)
    return jsonify(vuurwerk_info=new_list_info)


if __name__ == '__main__':
    app.run(host="192.168.2.9", port=80)
