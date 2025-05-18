import sqlite3
import logging
import sys
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Count the number of db connections
db_call_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_call_count 
    db_call_count += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get the total number of posts
def get_no_of_posts():
    connection = get_db_connection()
    no_of_posts = connection.execute('SELECT count(*) FROM posts').fetchone()  
    # The fetchone() method retrieves the first row of the result set. Hence, no_of_posts will be a single-element tuple
    # if there is at least one row in the posts table. For example, if there are 5 posts, no_of_posts will be (5,).
    connection.close()
    return no_of_posts

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info(f'Article ID not found: {post_id}')
        return render_template('404.html'), 404
    else:
        title = post['title']
        app.logger.info(f'Article retrieved: {title}')
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('Page retrieved: About Us')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info(f'New article created: {title}')
            return redirect(url_for('index'))

    return render_template('create.html')

# Define health checks for the website by an HTTP endpoint
@app.route('/healthz')
def healthcheck():
    response = app.response_class(
        response=json.dumps({'result': 'OK - healthy'}),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('Health check request successful')
    return response

# Define metrics for the website by an HTTP endpoint
@app.route('/metrics')
def metrics():
    no_of_posts = get_no_of_posts()
    count_value = no_of_posts[0] if no_of_posts else 0  
    response = app.response_class(
        response=json.dumps({"status":"success","code":0,"data":{'db_connection_count': db_call_count, 'post_count': count_value}}),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('Metrics request successful')
    return response
                         
# start the application on port 3111
if __name__ == "__main__":
    # Define StreamHandlers for stdout and stderr
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    handlers = [stdout_handler, stderr_handler]

    # Define basic configuration for the log messages
    logging.basicConfig(
    level=logging.DEBUG,
    format= '[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    handlers=handlers
    )
    app.run(host='0.0.0.0', port='3111', debug=True)
