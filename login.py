from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

    
engine = create_engine('sqlite:///user.db')

# Create a base class for declarative SQLAlchemy models
Base = declarative_base()

class Login(db.Model):
    __tablename__ = 'login'
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), nullable = False, unique = True)
    password = db.Column(db.String(24), nullable = False)
    

with app.app_context():
    db.create_all()
    
Base.metadata.create_all(engine)


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')
    

if __name__ == '__main__':
    app.run(debug=True, port=8000)