import hashlib
from flask import Flask, request, render_template_string
import sqlite3
import json

def send_flag():   
    with open('flag.txt', 'r') as m:
        data=m.read().strip()
    return json.dumps({'flag': data})

app = Flask(__name__)

def query_db(query):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        result = str(e)
    return result

@app.route('/')
def home():
    return render_template_string('''
        <html>
        <head>
            <title>SQLi</title>
            <style>
            body { 
                font-family: 'Courier New', Courier, monospace; 
                background-color: #0e0e0e; 
                color: #0f0;
                text-align: center; 
                padding: 50px; 
            }
            .navbar {
                background-color: #333;
                padding: 10px;
                color: #0f0;
            }
            form { 
                background-color: #222; 
                padding: 30px; 
                border-radius: 8px; 
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.7); 
                display: inline-block;
            }
            label {
                color: #0f0;
                font-weight: bold;
            }
            input[type=text], input[type=password] { 
                margin: 10px 0; 
                padding: 10px; 
                width: 200px; 
                border-radius: 4px; 
                border: 1px solid #0a0; 
                background: #000;
                color: #0f0;
            }
            input[type=submit] { 
                padding: 10px 20px; 
                background-color: #005500; 
                border: none; 
                border-radius: 4px; 
                color: #0f0; 
                cursor: pointer; 
            }
            input[type=submit]:hover { 
                background-color: #007700; 
            }
        </style>
        </head>
        <body>
            <form action="/login" method="post">
                <h2>Secure login</h2>
                <div>
                    <label>Username</label><br>
                    <input type="text" name="username"><br>
                </div>
                <div>
                    <label>Password</label><br>
                    <input type="password" name="password"><br>
                </div>
                <input type="submit" value="Login">
            </form>
        </body>
        </html>
    ''')

def IsloggedIn(bool):
    if bool is True:
        return render_template_string('''<h1>Logged in!</h1>
            <style>
            body {
                font-family: 'Courier New', Courier, monospace;
                background-color: #0e0e0e;
                color: #0f0;
                text-align: center;
                padding: 50px;
            }
            .flag-container {
                background-color: #222;
                border-radius: 10px;
                padding: 20px;
                display: inline-block;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.7);
                margin-top: 20px;
            }
            .flag {
                font-size: 1.5em;
                font-weight: bold;
                letter-spacing: 2px;
                word-wrap: break-word;
            }
        </style>
        <div class="flag-container">
            <div class="flag">{{flag}}</div>
        </div>
    ''', flag=send_flag())




@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = query_db(query)
    if result:
        return IsloggedIn(True)
    else:
        return 'Login failed!'
    
if __name__ == '__main__':
    app.run(debug=True)