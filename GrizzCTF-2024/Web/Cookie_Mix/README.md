# Cookie Mix (150 Points)


```python
from flask import Flask, render_template, request, url_for, redirect, make_response, flash, session
import random
app = Flask(__name__)
flag_value = open("./flag.txt").read().rstrip()
title = "Bad Authorization"
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
    app.run()
```

This challenge presents a flask website with a simple form to input a "secret cookie" to bypass authorization using a forged cookie + the guessed secret. Each time the page is reloaded a new cookie is used. The goal of this challenge is to bypass authorization using a forged cookie. 

#### Build/Deployment instructions
1. cd into the `src/app` directory where the Dockerfile is.
`cd Cookie_Mix/src/app`
2. Build the image
`docker build -t cookie-mix .`
3. Deploy the image
`docker run -p 3333:3333 -dit --name cookies cookie-mix:latest`
##### Resources Used
- [Flask Session Cookie Tampering (StackOverflow)](https://stackoverflow.com/questions/77340063/flask-session-cookie-tampering)
- [Flask-unsign](https://github.com/Paradoxis/Flask-Unsign)
- [Flask Session Cookie Manager](https://github.com/noraj/flask-session-cookie-manager)


###### Challenge Inspiration
- [MostCookies - PicoCTF Writeup](https://github.com/ZeroDayTea/PicoCTF-2021-Killer-Queen-Writeups/blob/main/WebExploitation/MostCookies.md)
