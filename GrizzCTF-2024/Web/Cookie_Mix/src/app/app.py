from flask import Flask, render_template, request, url_for, redirect, make_response, flash, session
import random
app = Flask(__name__)
flag_value = open("./flag.txt").read().rstrip()
title = "Cookie Mix"
# Updated list with the provided 'passwords'
cookie_passwords = [
    "fatoubah",
    "JAGER5",
    "International13",
    "aaron5797",
    "943761943761",
    "leon4me",
    "foru34",
    "melo33",
    "gabyboss10",
    "rockerswild",
    "cookiejuan",
    "cookietwo",
    "cookieThree",
    "cookieFour"
]

app.secret_key = random.choice(cookie_passwords)


@app.route("/")
def main():
    if session.get("very_auth"):
        check = session["very_auth"]
        if check == "blank":
            return render_template("index.html", title=title)
        else:
            return make_response(redirect("/display"))
    else:
        resp = make_response(redirect("/"))
        session["very_auth"] = "blank"
        return resp

@app.route("/search", methods=["GET", "POST"])
def search():
    if "name" in request.form and request.form["name"] in cookie_passwords:
        resp = make_response(redirect("/display"))
        session["very_auth"] = request.form["name"]
        return resp
    else:
        message = "That doesn't appear to be a valid entry."
        category = "danger"
        flash(message, category)
        resp = make_response(redirect("/"))
        session["very_auth"] = "blank"
        return resp

@app.route("/reset")
def reset():
    resp = make_response(redirect("/"))
    session.pop("very_auth", None)
    return resp

@app.route("/display", methods=["GET"])
def flag():
    if session.get("very_auth"):
        SessionCheck = session["very_auth"]
        if SessionCheck == "admin":
            resp = make_response(render_template("flag.html", value=flag_value, title=title))
            return resp
        flash("That is a valid entry! Not very special though...", "success")
        return render_template("not-flag.html", title=title, cookie_name=session["very_auth"])
    else:
        resp = make_response(redirect("/"))
        session["very_auth"] = "blank"
        return resp

if __name__ == "__main__":
    app.run(debug=True)






