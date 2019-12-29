from flask import Flask, render_template, redirect, request, url_for, flash, session
import os
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
# import env as config

app = Flask(__name__)

# configuration of Database
# dev
# app.config['MONGO_URI'] = config.MONGO_URI
# app.config['SECRET_KEY'] = config.SECRET_KEY

app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

bcrypt = Bcrypt(app)

mongo = PyMongo(app)


@app.route('/')
def index():
    if 'username' in session:
        mongo.db.users.find_one({"username": session['username']})
        flash(f"Welcome, you are logged in as username:  {session['username']}", 'success')    
    return render_template('index.html')

"""
Users / Log-in / Register
"""
# Register
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST': 
        existing_user = mongo.db.users.find_one({'username' : request.form['username']})    

        if existing_user is None:
            hashpass = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            if request.form.get('teacher'):
                user_type = 'teacher'
            if request.form.get('parent'):
                user_type = 'parent'
            mongo.db.users.insert_one({
                'firstname': request.form['firstname'].capitalize(),
                'lastname': request.form['lastname'].capitalize(),    
                'email': request.form['email'],                            
                'username': request.form['username'],
                'password': hashpass,
                'user_type': user_type.capitalize(),
                'admin': False})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            flash(f"Sorry username, {request.form['username']} already exists", 'danger')

    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_user = mongo.db.users.find_one(
            {'username': request.form['username']})

        if login_user:
            if bcrypt.check_password_hash(login_user['password'], (request.form['password']).encode('utf-8')):
                session['username'] = request.form['username']
                return redirect(url_for('index'))
        else:
            flash(f"Sorry username or password invalid", 'danger')

    return render_template('login.html')

# logout
@app.route('/logout')
def logout():
    if 'username' in session:
        session.clear()
        flash(f'You are now logged out', 'success')
    return redirect(url_for('login'))

# Profile
@app.route('/profile')
def profile():
    if 'username' in session:
        user = mongo.db.users.find_one({"username": session['username']})
        return render_template("profile.html", user=user, user_id=user['_id'])     
    return redirect(url_for('index'))


#storybook
@app.route('/storybook')
def storybook():
    return render_template('storybook.html')

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=os.environ.get('PORT'),
            debug=False)
