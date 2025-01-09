from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

USERNAME = app.config['USERNAME']
PASSWORD = hashlib.sha256(app.config['PASSWORD'].encode('utf-8')).hexdigest()
FLAG = app.config['FLAG']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flag')
def flag():
    if session.get('Authenticated') is not True:
        return redirect(url_for('login'))
    else:
        return render_template('flag.html', flag=FLAG)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
        if username and password:
            if username == USERNAME and password == PASSWORD:
                session['Authenticated'] = True
                return redirect(url_for('flag'))
            else:
                return "Invalid Credentials"
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)  


















