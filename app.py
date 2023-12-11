from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import pymysql.cursors

app = Flask(__name__)
app.config["SECRET_KEY"] = "438324438324438324"
app.secret_key = app.config["SECRET_KEY"]


def read_global_code():
    f = open("static/code.txt", "r")
    glob_code = f.read()
    f.close()
    return glob_code


def write_global_code(glob_code):
    f = open("code.txt", "w")
    f.write(glob_code)
    f.close()


def connect_to_database():
    connection = None
    try:
        connection = pymysql.connect(host='192.168.2.171',
                                     user='Hubo',
                                     password='Hubo2015',
                                     database="videos",
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection
    except pymysql.Error as e:
        print(f"Error while connecting to MySQL database: {e}")
    finally:
        if connection is not None:
            print(f"Connection to the database was successful")
            return connection
        else:
            return ConnectionError




@app.before_request
def before_request():
    if "code" in session:
        write_global_code(session["code"])


@app.route("/drop")
def drop_session():
    session.clear()
    write_global_code(str(0))
    return redirect(url_for("index"))


@app.route('/_get_video', methods=['GET'])
def get_video():
    code = read_global_code()
    if code != 0:
        print(f"code: {code}")
        connection = connect_to_database()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM `videos` WHERE `code` = %s",
                               [code])
                vuurwerk_info = cursor.fetchone()
                # naam = vuurwerk_info["naam"]
                vid = vuurwerk_info["vid"]
                # img = vuurwerk_info["img"]
                start = vuurwerk_info["start"]
                duration = vuurwerk_info["duration"]
                print(f"vid: {vid}")
        return jsonify(video=f"https://www.youtube-nocookie.com/embed/{vid}&start={start}&autoplay=1&mute=1",
                       duration=duration)
    return jsonify(video="None", duration=2500)


@app.route('/player', methods=('GET', 'POST'))
def player():
    return render_template('Video_Player.html')


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.args.get("code") is not None:
        code = request.args.get("code")
        print(code)
        write_global_code(code)
    return render_template('Video_Selecter.html')


@app.route('/test', methods=('GET', 'POST'))
def test():
    vuurwerk_list = [
        ["501", "test 1", "youtube.com/test1"],
        ["502", "test 2", "youtube.com/test2"],
    ]
    return render_template('test.html')


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
    app.run(host="192.168.2.130", port=80)
