from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from gevent.pywsgi import WSGIServer
from gevent import monkey
monkey.patch_all()
app = Flask(__name__)
app.secret_key = os.urandom(24)

posts = [
    {'id': 1, 'title': 'First Post', 'content': 'Welcome to the bliggity blog!'},
    {'id': 2, 'title': 'Bing', 'content': 'Another bliggity blog post II'},
    {'id': 3, 'title': 'Bong', 'content': 'Yet another bliggity blog post III'},
    {'id': 4, 'title': 'LOOK UP', 'content': 'Bliggity blog post IIII'},
    {'id': 5, 'title': 'Retro Gaming', 'content': 'Discuss your favorite retro games and consoles.'},
    {'id': 6, 'title': 'Why PlayStation 1?', 'content': 'The PS1 has a special place in our hearts.'},
    {'id': 7, 'title': 'The Golden Age', 'content': 'A look back at the golden age of video games.'},
    {'id': 8, 'title': 'Arcades Forever', 'content': 'Let\'s remember the arcades of the 80s and 90s.'},
    {'id': 9, 'title': 'Game Development in the 90s', 'content': 'A deep dive into how games were made back then.'},
    {'id': 10, 'title': 'Sonic vs Mario', 'content': 'The great rivalry between Sonic and Mario games.'},
    {'id': 11, 'title': 'Where\'s the Flag?', 'content': 'Hint: This might be a secret post!'},
    {'id': 12, 'title': 'The Evolution of Consoles', 'content': 'From Atari to PlayStation, a timeline of consoles.'},
    {'id': 13, 'title': '1995 E3 Event', 'content': 'The year the PlayStation changed everything.'},
    {'id': 14, 'title': 'Handheld Consoles', 'content': 'Exploring the rise of handheld consoles like Game Boy.'},
    {'id': 15, 'title': 'Secrets in Games', 'content': 'Remember those hidden easter eggs and cheat codes?'},
    {'id': 16, 'title': 'Retro Remakes', 'content': 'How modern remakes of classic games measure up.'},
    {'id': 17, 'title': 'Game Collecting', 'content': 'The growing culture of collecting retro games.'},
    {'id': 18, 'title': 'Top 10 PS1 Games', 'content': 'Our countdown of the best PS1 games.'},
    {'id': 19, 'title': 'Best Game Soundtracks', 'content': 'A tribute to the unforgettable music of retro games.'},
    {'id': 20, 'title': 'PlayStation Memories', 'content': 'Share your favorite PlayStation gaming memories.'}
]


comments = {
    1: [],
    2: [],
    3: [],
    4: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: [],
    9: [],
    10: [],
    11: [],
    12: [],
    13: [],
    14: [],
    15: [],
    16: [],
    17: [],
    18: [],
    19: [],
    20: []
}

FLAG = open("flag.txt", "r").read().strip()
@app.before_request
def simulate_admin():
    if request.endpoint == 'admin_flag':
        session['admin'] = True
    else:
        session['admin'] = False

@app.route('/')
def index():
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        return 'Post not found', 404
    post_comments = comments.get(post_id, [])
    return render_template('post.html', post=post, comments=post_comments)

@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    content = request.form.get('content')
    if content:
        comments.setdefault(post_id, []).append(content)
    return redirect(url_for('post', post_id=post_id))

@app.route('/admin/flag')
def admin_flag():
    if 'admin' in session and session['admin']:
        return jsonify({"flag":FLAG})
    else:
        return 'Unauthorized', 403

def simulate_admin_reading():
    with app.test_request_context():
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['admin'] = True
            for post in posts:
                client.get(url_for('post', post_id=post['id']))

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 9898), app)
    print("Starting server on http://0.0.0.0:9898")
    http_server.serve_forever()
