from flask import Flask, send_file, render_template, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/flag.txt')
def serve_flag():
    return send_file('flag.txt', as_attachment=True)


@app.route('/arigato')
def arigato():
    flag_url = url_for('serve_flag')
    return f'<p><a href="{flag_url}">flag.txt</a></p>'

@app.route('/fileupload')
def FileUpload():
    return render_template('fileupload.html')

@app.route('/robots.txt')
def serve_robots():
    return send_file('robots.txt')

if __name__ == '__main__':
    app.run(debug=True)