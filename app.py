from flask import Flask, flash, render_template, redirect, url_for, flash, make_response, request
from flask_bootstrap import Bootstrap
from static.forms.login import LoginForm
from static.forms.signups import SignUpForm
import pymysql
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
boostrap = Bootstrap(app)
app.config['SECRET_KEY'] = secrets.token_hex(20) #el parámetro indica la cantidad de bytes a utilizar
#secrets_token_urlsafe(xx) otro método para crear una clave secreta, crea un token para que arruine la url

def connection():
    return pymysql.connect(
        host= 'localhost',
        user= 'root',
        password= 'admin',
        db = 'db_python_crud'
        )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    loginf= LoginForm()
    
    if loginf.validate_on_submit():
        email = loginf.email.data
        password = loginf.password.data
        conn = connection()
        cursor = conn.cursor()
        encontrado, registro = found(email, cursor)
        conn.close()
        if encontrado:
            user_pass = registro[3]
            pass_ok = check_password_hash(user_pass, password)
            if pass_ok:
                id = str(registro[0])
                my_response = make_response(redirect('/profile'))
                my_response.set_cookie('user_id', bytes(id, 'utf8'))
                my_response.set_cookie('username', bytes(registro[1], 'utf8'))
                my_response.set_cookie('user_email', bytes(registro[2], 'utf8'))
                return my_response
            else:
                flash('Datos ingresados incorrectos.')
        else:
            flash('Datos ingresados incorrectos.')
            loginf.email.data = ''
            loginf.password.data = ''
            return render_template('login.html', form = loginf)

    return render_template('login.html', form = loginf)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signf= SignUpForm()
    if signf.validate_on_submit():
        nom = signf.nombre.data
        email = signf.email.data
        password = generate_password_hash(signf.password.data)
        conn = connection()
        cursor = conn.cursor()
        encontrado, us = found(email, cursor)
        if encontrado:
            signf = SignUpForm()
            flash('Ese usuario ya existe')
            signf.email.data = ''
            return render_template('signup.html', form = signf)
        else:
            sql = 'INSERT INTO usuarios(username, email, password) VALUES (%s, %s, %s)'
            values = (nom, email, password)
            cursor.execute(sql, values)
            conn.commit()
            conn.close()
            flash('Usuario creado con éxito', 'info')
            return redirect(url_for('login'))

    return render_template('signup.html', form = signf)

@app.route('/profile')
def profile():
    context = {}
    if 'user_id' in request.cookies:
        user_id = request.cookies.get('user_id')
        username = request.cookies.get('username')
        user_email = request.cookies.get('user_email')
        context = {
            'user_id': user_id,
            'username': username,
            'user_email': user_email
        }
    else: 
        return redirect(url_for('login'))

    return render_template('profile.html', **context)

@app.route('/logout')
def logout():
    if 'user_id' in request.cookies:
        username = request.cookies.get('username')
        my_response = make_response(render_template('logout.html', nom = username))
        my_response.delete_cookie('user_id')
        my_response.delete_cookie('username')
        my_response.delete_cookie('user_email')
        return my_response
    else:
        return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(error):
    return 'Error 404'

@app.errorhandler(500)
def server_error(error):
    return 'Error 500'

def found(email, cursor):
    found = False
    cursor.execute('SELECT * FROM usuarios WHERE email = %s', email)
    reply = cursor.fetchall()
    if len(reply) != 0:
        found = True
        reply = reply[0]
    else:
        found = False
        reply = ()
    return found, reply

if __name__ == '__main__':
    app.run(debug=True)