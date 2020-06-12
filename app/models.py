from app import db, login, Config
from flask_login import UserMixin
from oauthlib.oauth2 import WebApplicationClient


class User(UserMixin, db.Model):
    id = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String(), index=True, unique=True)
    profile_pic = db.Column(db.String())
    twilio_number = db.Column(db.String())

    def __init__(self, id, name, email, profile_pic):
        self.id = id
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

    def add_attrs(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f'<User> {self.name}'


@login.user_loader
def load_user(id):
    return User.query.get(id)
