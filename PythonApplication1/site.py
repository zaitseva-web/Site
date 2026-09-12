from flask import Flask, render_template, request, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' # for session management, replace with a secure key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///organizer.db'
db = SQLAlchemy(app)
#model for storing user information
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    lists = db.relationship('Group', backref='user', lazy=True)
#model for storing group information
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.relationship('Item', backref='group', cascade='all, delete-orphan', lazy=True)
#model for items in the group
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

#create the database at the first run
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    #check if user is logged in
    username = session.get('username')
    lists = []
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            lists = Group.query.filter_by(user_id=user.id).all()
    return render_template('index.html', username=username, lists=lists)

@app.route('/create_list', methods=['POST'])
def create_list():
    username = session.get('username')
    print('Debug: Username from session:', username)  # Debugging line
    if not username:
        return redirect(url_for('login'))
    name = request.form.get('list_name')
    print('Debug: List name from form:', name)  # Debugging line
    user = User.query.filter_by(username=username).first()
    print('Debug: User found:', user)  # Debugging line
    if name and user:
        new_list = Group(name=name, user_id=user.id)
        db.session.add(new_list)
        db.session.commit()
        print('successfully added new list')  # Debugging line
   
        if request.headers.get('HX-Request'):
            return render_template('list_card.html', new_list=new_list)
        else:
            return redirect(url_for('lists'))
    else:
        print('Failed to add new list: name or user is None')  # Debugging line
    return redirect(url_for('home'))
@app.route('/add_item/<int:list_id>', methods=['POST'])
def add_item(list_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    text = request.form.get('text')
    print('debug item:', text)  # Debugging line
    print('debug list_id:', list_id)  # Debugging line
    if text:
        new_item = Item(text=text, group_id=list_id)
        db.session.add(new_item)
        db.session.commit()
        print('successfully added new item')  # Debugging line
        if request.headers.get('HX-Request'):
            return render_template('item_card.html', new_item=new_item)
    return redirect(url_for('inside_list', list_id=list_id))

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
@app.route('/lists')
def lists():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=username).first()
    if user:
        user_lists = Group.query.filter_by(user_id=user.id).all()
        return render_template('lists.html', lists=user_lists, username=username)
    return redirect(url_for('home'))
@app.route('/inside_list')
def inside_list():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    list_id = request.args.get('list_id')
    group = Group.query.get_or_404(list_id)
    items = group.items
    return render_template('inside_list.html', group=group, items=items, username=username)
@app.route('/delete_list/<int:list_id>', methods = ['POST'])
def delete_list(list_id):
    username = session.get('username')
    if not username:
        return redirect('login')
    list_to_delete = Group.query.get_or_404(list_id)
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for('lists'))
@app.route('/delete_item/<int:item_id>', methods = ['POST'])
def delete_item(item_id):
    username = session.get('username')
    if not username:
        return redirect('login')
    item_to_delete = Item.query.get_or_404(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('lists'))

if __name__ == '__main__':
    app.run(debug=True)