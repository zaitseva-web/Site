from flask import Flask, render_template, request, session, url_for
app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session['name'] = request.form.get('user_input')
    name = session.get('name', 'Guest')
    return render_template('index.html', name=name)

@app.route('/about')
def about():
    name = session.get('name', 'Guest')
    return render_template('about.html', name=name)
