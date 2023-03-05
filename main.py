from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///text.db'
app.config['SECRET_KEY'] = '63103453574bccae5541fa05'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key = True)
    email = db.Column(db.String(), unique = True, nullable = False)
    username = db.Column(db.String(), unique = True, nullable = False)
    password = db.Column(db.String(), nullable = False)
    tag = db.Column(db.Integer(), nullable = False)
    combo = db.Column(db.String(), nullable = False)
    friendships = db.relationship('Friendship', foreign_keys='Friendship.user_id', backref='user', lazy=True)    

    

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)




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
            
        user = User(email=email, username=username, password=psw, tag=tag, combo = combo)
        db.session.add(user)
        db.session.commit()


    return render_template('register.html')

@app.route('/profile',  methods=['POST', 'GET'])
def profile():
    message = ''
    if request.method == 'POST':
        friend_combo = request.form.get('friend')
        if friend_combo:
            friend = User.query.filter_by(combo=friend_combo).first()
            if friend:
                message = 'Added'
    return render_template('profile.html', message=message)


@app.route('/login',  methods=['POST', 'GET'])
def login():
    email = request.form.get("email")
    password = request.form.get('password')
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        username = user.username
        tag = user.tag
        combo = user.combo
        session['username'] = username
        session['tag'] = tag
        session['combo'] = combo
        return redirect(url_for('profile'))
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)