from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    score = db.Column(db.Integer, default= 0)
    admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(140), index=True, unique=True)
    answers = db.Column(db.String(140))
    correct_answer = db.Column(db.String(140))
    speed =  db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Question {}'.format(self.question)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
