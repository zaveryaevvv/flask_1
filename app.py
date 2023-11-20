import requests
from flask import Flask, render_template, url_for, request, jsonify,redirect, session, flash
import mysql.connector
from mysql.connector import Error
import json
from config import db_config, cl , dd


app = Flask(__name__)
app.config['SECRET_KEY'] = dd



def create_connection_mysql_db(db_host, user_name, user_password, db_name):
    connection_db = None
    try:
        connection_db = mysql.connector.connect(
            host = db_host,
            user = user_name,
            passwd = user_password,
            database = db_name
        )
        print("Подлючение к MySQL успешно выполнено")

    except Error as db_connection_error:
        print("Возникла ошибка: ", db_connection_error)
    return connection_db




@app.route('/process_data', methods=["POST"])
def save():
    if 'logged_in' in session:
        conn = create_connection_mysql_db(
        db_config["mysql"]["host"],
        db_config["mysql"]["user"],
        db_config["mysql"]["passwd"],
        db_config["mysql"]["db"])
        cursor = conn.cursor()
        data = json.dumps(request.json)
        user_key = session['key']
        sqlFormula = "UPDATE `test` SET `data`= %s WHERE `login_key` = %s"
        cursor.execute(sqlFormula, [data, user_key])
        cursor.fetchall()
        conn.commit()

        return render_template("index.html")
    else:
        return redirect('/')
    



@app.route('/get_data', methods=["POST"])
def get_data():
    if 'logged_in' in session:
        conn = create_connection_mysql_db(
        db_config["mysql"]["host"],
        db_config["mysql"]["user"],
        db_config["mysql"]["passwd"],
        db_config["mysql"]["db"])
        cursor = conn.cursor()


        user_key = session['key']
        sqlFormula = "SELECT `data` FROM `test` WHERE `login_key` = %s"
        cursor.execute(sqlFormula, [user_key])
        result = cursor.fetchall()
        conn.commit()
        result = result[0][0]
        result = json.loads(result)

        params = {'words' : result['words'],
                  'names' : result['names'],
                  'channel_id' : result['channel_id']
                }
        return jsonify(params)
    else:
        return redirect('/')
    



@app.route('/', methods=["POST", "GET"])
def index():
    return render_template("index.html")


@app.route('/login', methods=["POST"])
def login():
    conn = create_connection_mysql_db(
    db_config["mysql"]["host"],
    db_config["mysql"]["user"],
    db_config["mysql"]["passwd"],
    db_config["mysql"]["db"])
    cursor = conn.cursor()

    user_key = request.form["key-pass"]
    sqlFormula = "SELECT * FROM test WHERE `login_key` = %s"
    cursor.execute(sqlFormula, [user_key])

    results = cursor.fetchall()


    if len(results) > 0:
        session['logged_in'] = True
        session['key'] = user_key
        return redirect('/dashboard')

    else:
        session.pop('logged_in', None)
        session.pop('key', None)
        flash('НЕВЕРНЫЙ КЛЮЧ АВТОРИЗАЦИИ', 'error')
        return redirect('/')
    
@app.route('/dashboard', methods=["GET"])
def dashboard():
    if 'logged_in' in session:
        return render_template("dashboard.html")

    else:
        return redirect('/')
    


@app.route('/settings')
def settings():
    if 'logged_in' in session:
        return render_template("settings.html")
    else:
        return redirect('/')
    


@app.route('/start-request', methods=["POST"])
def search_req():
    if 'logged_in' in session:
        data_from_client = request.get_json()  # Get json data from cliend

        req = requests.post(cl, json=data_from_client)
        return jsonify(req.json())

    else:
        return redirect('/')

    

@app.route('/names')
def names():
    if 'logged_in' in session:
        return render_template("names.html")
    else:
        return redirect('/')





if __name__ == "__main__":
    app.run( port=5000,debug=True)