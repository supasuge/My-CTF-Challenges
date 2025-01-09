from flask import Flask, render_template, request
from models import Game
from database import db_session, init_db
from sqlalchemy import text
from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        search = ""
        order = None
        if "search" in request.form:
            search = request.form["search"]
        if "order" in request.form:
            order = request.form["order"]
        if order is None:
            games = Game.query.filter(Game.title.like("%{}%".format(search)))
        else:
            games = Game.query.filter(
                Game.title.like("%{}%".format(search))
            ).order_by(text(order))
        return render_template("index.html", games=games)
    else:
        games = Game.query.all()
        return render_template("index.html", games=games)

if __name__ == "__main__":
    http_server = WSGIServer(('0.0.0.0', 4000), app)
    http_server.serve_forever()
    