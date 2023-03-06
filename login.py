from main import app, db, Friendship

with app.app_context():
    friendships = Friendship.query.all()
    
