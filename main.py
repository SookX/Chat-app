from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import random
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///text.db'
app.config['SECRET_KEY'] = '63103453574bccae5541fa05'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key = True)
    email = db.Column(db.String(), unique = True, nullable = False)
    username = db.Column(db.String(), unique = True, nullable = False)
    password = db.Column(db.String(), nullable = False)
    tag = db.Column(db.Integer(), nullable = False)
    combo = db.Column(db.String(), nullable = False)
    

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    combo1 = db.Column(db.String,  nullable=False)
    combo2 = db.Column(db.String, nullable = False)

    def __init__(self, combo1, combo2):
        self.combo1 = combo1
        self.combo2 = combo2

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String, nullable=False)
    receiver = db.Column(db.String, nullable = False)
    text = db.Column(db.String(), nullable=False)
    now = datetime.datetime.now()
    date_string = now.strftime('%Y-%m-%d %H:%M:%S')
    date = db.Column(db.String(), default=date_string)


@app.route('/')
def home():
    return render_template('index.html')



@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        psw = request.form.get("password")
        psw_confirm = request.form.get("confirm_password")
        if User.query.filter_by(username=username).first():
            return render_template('register.html', message="Username already exists.")
        if User.query.filter_by(email=email).first():
            return render_template('register.html', message="Another account is using this email.")
        if psw != psw_confirm:
            return render_template('register.html', message="The passwords does not match.")
        
        tag = random.randint(0, 9999)
        combo = username + "#" + str(tag)

        hashed_psw = bcrypt.generate_password_hash(psw).decode('utf-8')
            
        user = User(email=email, username=username, password=hashed_psw, tag=tag, combo = combo)
        db.session.add(user)
        db.session.commit()
        session['username'] = username
        session['tag'] = tag
        session['combo'] = combo
        return redirect(url_for('profile'))

    return render_template('register.html')

@app.route('/profile',  methods=['POST', 'GET'])
def profile():
    message = ''
    username = session.get('username')
    add = request.form.get('add', False)
    combo = session.get('combo')
    if request.method == 'POST':
        if add != False:
            friend_combo = request.form.get('friend')
            if friend_combo:
                friend = User.query.filter_by(combo=friend_combo).first()
                if friend:
                    existing_friendship = Friendship.query.filter(
                    (Friendship.combo1 == combo) & (Friendship.combo2 == friend_combo)
                    ).first()
                    if existing_friendship:
                        message = "Friendship already exists."
                    else:
                        new_friendship = Friendship(combo1=combo, combo2=friend_combo)
                        db.session.add(new_friendship)
                        db.session.commit()
                        new_friendship = Friendship(combo2=combo, combo1=friend_combo)
                        db.session.add(new_friendship)
                        db.session.commit()
    friends = Friendship.query.filter(Friendship.combo1 == combo)
    return render_template('profile.html', combo=combo, friends = friends)



@app.route('/login',  methods=['POST', 'GET'])
def login():
    email = request.form.get("email")
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        username = user.username
        tag = user.tag
        combo = user.combo
        session['username'] = username
        session['tag'] = tag
        session['combo'] = combo
        return redirect(url_for('profile'))
    return render_template('login.html')

@app.route('/chat/<string:current_friend>', methods=['POST', 'GET'])
def chat(current_friend):
    combo = session.get('combo')
    msg = request.form.get('message')
    send = request.form.get('send', False)
    if send != False:
        if request.method == "POST":
            message = Message(sender = combo, receiver = current_friend, text = msg)
            db.session.add(message)
            db.session.commit()
            return redirect(request.url)
    messages = Message.query.filter(
        ((Message.sender == combo) & (Message.receiver == current_friend)) |
        ((Message.sender == current_friend) & (Message.receiver == combo))
    ).order_by(Message.date.asc()).all()


    
    return render_template('chat.html', current_friend=current_friend, combo=combo, messages=messages)

@app.route('/sign-out')
def sign_out():
    session.pop("username", None)
    session.pop("tag", None)
    session.pop("combo", None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=8000)