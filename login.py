from main import app, db, Friendship

with app.app_context():
    db.create_all()    
