from flask import Flask, render_template, request, session, url_for
app = Flask(__name__)
app.secret_key = 'your_secret_key' # for session management, replace with a secure key in production

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

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    messadge_statuse = ''
    if request.method == 'POST':
        user_name = request.form.get('name')
        user_message = request.form.get('message')
        # Here you would typically handle the message, e.g., save it to a database or send an email
        print(f"Received message from {user_name}: {user_message}")
        messadge_statuse = 'Message sent successfully!'
    return render_template('contact.html', messadge_statuse=messadge_statuse)

if __name__ == '__main__':
    app.run(debug=True)