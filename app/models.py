from app import db, login
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String(), index=True, unique=True)
    profile_pic = db.Column(db.String())
    twilio_number = db.Column(db.String(), unique=True)

    def __repr__(self):
        return f'<User> {self.name}'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
