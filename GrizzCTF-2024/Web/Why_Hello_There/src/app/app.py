from flask import Flask, render_template_string, request, url_for

app = Flask(__name__)

@app.route('/')
def index():
    name = request.args.get('name', 'CTF Player')
    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bubbles Blog</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
        <style>
            body, html {{
                height: 100%;
                margin: 0;
                font-family: 'Roboto', sans-serif;
                background-color: #fff;
                color: #333;
            }}
            header, footer {{
                background-color: #2c3e50; /* Dark shade of blue */
                color: #fff;
                padding: 20px 0;
                text-align: center;
            }}
            nav ul {{
                list-style-type: none;
                padding: 0;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            nav ul li {{
                margin: 0 15px;
            }}
            nav ul li a {{
                color: #ecf0f1;
                text-decoration: none;
                font-weight: bold;
                font-size: 18px;
                transition: color 0.3s;
            }}
            nav ul li a:hover {{
                color: #bdc3c7;
            }}
            section {{
                margin: 50px auto;
                max-width: 1200px;
                text-align: center;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            p, a {{
                color: #333;
                transition: color 0.3s;
            }}
            a:hover {{
                color: #2c3e50;
            }}
            .post-card {{
                flex: 0 1 calc(33.333% - 40px); /* Three cards per row, accounting for margin */
                margin: 20px;
                padding: 20px;
                background-color: #ecf0f1; /* Light gray background for cards */
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                transition: transform 0.3s, box-shadow 0.3s;
            }}
            .post-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
            }}
            .post-container {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
            }}
            .giphy-embed {{
                max-width: 100%;
                max-height: 150px;
                margin-bottom: 10px;
            }}
            @media (max-width: 768px) {{
                .post-card {{
                    flex: 0 1 calc(50% - 40px); /* Adjust for two cards per row on smaller screens */
                }}
            }}
            @media (max-width: 480px) {{
                .post-card {{
                    flex: 0 1 calc(100% - 40px); /* Full width for very small screens */
                }}
            }}
            .bear-image {{
                max-width: 100%;
                height: auto;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <header>
            <nav>
                <ul>
                    <li><a href="#home">Home</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#blog">Blog</a></li>
                </ul>
            </nav>

        </header>

        <section id="home">
            <h1>Welcome to Bubbles Blog</h1>
            <p>Hello {name}! This is a place where I share my thoughts and experiences... And memes, of course.</p>
        </section>

        <section id="about">
            <h2>About Me</h2>
            <p>I am a passionate writer and love to explore various topics. I enjoy long walks on the beach, but I can't see in the dark.</p>
        </section>

        <section id="blog">
            <h2>Latest Blog Posts</h2>
            <div class="post-container">
                <!-- Your existing post cards here -->
                <div class="post-card">
                    <h3>Tortoose VS. Torteese</h3>
                    <p>This is slightly more entertaining than the last start wars: <iframe src="https://giphy.com/embed/tj7q6n5L4qW7m" width="480" height="270" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></p>
                </div>
                <div class="post-card">
                    <h3>Monkey</h3>
                    <p>This is my best friend, Derrick: <iframe src="https://giphy.com/embed/Rlwz4m0aHgXH13jyrE" width="480" height="480" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></p>
                </div>
                <div class="post-card">
                    <h3>Tortoose, the turtle</h3>
                    <p>Another day, another dollar: <iframe src="https://giphy.com/embed/YqHMVSYXIMEiA" width="480" height="379" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></p>
                </div>
                <div class="post-card">
                    <h3>Beaking News Again....</h3>
                    <p>When in doubt Meme it out: <iframe src="https://giphy.com/embed/hvT5KWdFkUOklHCxXk" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></p>
                </div>
                <!-- Additional meme post cards -->
                <div class="post-card">
                    <h3>Code & Coffee</h3>
                    <p>How I start my day: <iframe src="https://giphy.com/embed/26hiu3mZVquuykwhy" width="480" height="288" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></p>
                </div>
                <div class="post-card">
                    <h3>Debugging Adventures</h3>
                    <p>The thrill of the hunt: <iframe src="https://giphy.com/embed/13HgwGsXF0aiGY" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></p>
                </div>
                <!-- New post card with the IrishBear.webp image -->
                
            </div>
        </section>

        <footer>
            <p>&copy; 2024 Bubbles Blog. All rights reserved.</p>
        </footer>
    </body>
    </html>
    ''')

if __name__ == "__main__":
    app.run(debug=True)
