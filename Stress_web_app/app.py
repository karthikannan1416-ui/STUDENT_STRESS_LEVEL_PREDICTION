from flask import Flask, render_template, request, redirect, session
import sqlite3
import numpy as np
import pickle
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

model = pickle.load(open("model.pkl", "rb"))

# DB INIT
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS stress_data(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    sleep REAL,
                    study REAL,
                    mobile REAL,
                    exercise REAL,
                    relax REAL,
                    prediction TEXT,
                    date TEXT,
                    time TEXT)''')

    conn.commit()
    conn.close()

init_db()

# LOGIN PAGE
@app.route('/')
def login():
    return render_template('login.html')

# SIGNUP
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    u = request.form['username']
    p = request.form['password']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users(username,password) VALUES (?,?)",(u,p))
    conn.commit()
    conn.close()

    return redirect('/')

# LOGIN CHECK
@app.route('/login', methods=['POST'])
def do_login():
    u = request.form['username']
    p = request.form['password']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p))
    user = c.fetchone()
    conn.close()

    if user:
        session['user'] = u
        return redirect('/dashboard')
    else:
        return "Invalid login"

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html')

# PREDICT
@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect('/')

    sleep = float(request.form['sleep'])
    study = float(request.form['study'])
    mobile = float(request.form['mobile'])
    exercise = float(request.form['exercise'])
    relax = float(request.form['relax'])

    data = np.array([[sleep, study, mobile, exercise, relax]])
    pred = model.predict(data)

    if pred[0] == 0:
        result = "Low Stress 😊"
        tip = "Maintain your healthy routine 👍"
    elif pred[0] == 1:
        result = "Moderate Stress 😐"
        tip = "Balance study and relaxation 🧘"
    else:
        result = "High Stress 😟"
        tip = "Sleep well, reduce mobile usage, exercise more 🏃"

    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%H:%M:%S")

    # Save to DB
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""INSERT INTO stress_data 
    (username,sleep,study,mobile,exercise,relax,prediction,date,time)
    VALUES (?,?,?,?,?,?,?,?,?)""",
    (session['user'],sleep,study,mobile,exercise,relax,result,date,time))
    conn.commit()
    conn.close()

    return render_template('result.html', prediction=result, tip=tip)

# HISTORY
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM stress_data WHERE username=?", (session['user'],))
    data = c.fetchall()
    conn.close()

    return render_template('history.html', data=data)

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)