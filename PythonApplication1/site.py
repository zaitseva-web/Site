from flask import Flask, render_template, request, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.secret_key = 'your_secret_key' # for session management, replace with a secure key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
#model for storing user information
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
#create the database at the first run
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    #check if user is logged in
    username = session.get('username')
    return render_template('index.html', username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        exiting_user = User.query.filter_by(username=username).first()
        if exiting_user:
            error = 'Username already exists'
        else:
            # Create a new user
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the user exists
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None) #delete the username from the session to log out the user
    return redirect(url_for('home'))

@app.route('/about')
def about():
    username = session.get('username')
    return render_template('about.html', username=username)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    messadge_statuse = ''
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_message = request.form.get('message')
        # Here you would typically handle the message, e.g., save it to a database or send an email
        print(f"Received message from {username}: {user_message}")
        messadge_statuse = 'Message sent successfully!'
    return render_template('contact.html', messadge_statuse=messadge_statuse, username=username)

if __name__ == '__main__':
    app.run(debug=True)