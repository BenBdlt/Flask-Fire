import imp
from flask import Blueprint, render_template, make_response, request, redirect, url_for, session
import os
import time
import pyrebase
import json
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps

from server.src import app

main = Blueprint("main", __name__)

cred = credentials.Certificate('creds.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('fbconfig.json')))


##### USERS #####

# MIDDLEWARE
def check_token(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if not request.headers.get('authorization'):
            return {'message': 'No token provided'},400
        try:
            user = auth.verify_id_token(request.headers['authorization'])
            request.user = user
        except:
            return {'message':'Invalid token provided.'},400
        return f(*args, **kwargs)
    return wrap


users = [{'uid': 1, 'name': 'ISMA MIG'}]

#API route to get users
@main.route('/userinfo')
@check_token
def userinfo():
    return {'data': users}, 200


#API route to sign up a new user
@main.route('/signup', methods=["GET", "POST"])
def signup():
    template = render_template('signup.html')
    # 2
    response = make_response(template)
    # 3
    response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
    
    email=request.form.get("mail-form")
    password=request.form.get("pswd-form")
    if request.method == "POST":
        if email is None or password is None:
            return {'message': 'Error missing email or password'},400
        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            # user = pb.auth().sign_in_with_email_and_password(email, password)
            return redirect(url_for('main.profile'))
            # return {'message': 'OUI'},200
        except:
            return {'message': 'Error creating user'},400
    
    return response
    
#LOGIN
@main.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get("mail-form")
        password = request.form.get("pswd-form")
        user = pb.auth().sign_in_with_email_and_password(email, password)
        user = pb.auth().refresh(user['refreshToken'])
        user_id = user['idToken']
        # session['usr'] = user_id
        return redirect(url_for('main.profile', actual_user=user_id))
    return render_template('login.html')


#Api route to get a new token for a valid user
@app.route('/token')
def token():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user['idToken']
        return {'token': jwt}, 200
    except:
        return {'message': 'There was an error logging in'},400





##################

def format_server_time():
  server_time = time.localtime()
  return time.strftime("%I:%M:%S %p", server_time)
  
@main.route('/')
def index():
    context = { 'server_time': format_server_time() }
    # 1
    template = render_template('index.html', context=context)
    # 2
    response = make_response(template)
    # 3
    response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
    return response

@main.route('/profile')
def profile():
    return render_template('profile.html')
    # template = render_template('profile.html')
    # # 2
    # response = make_response(template)
    # # 3
    # response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
    # return response