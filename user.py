from flask import current_app
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, name, userName, eMail, password):

        self.name = name
        self.userName = userName
        self.email    = eMail
        self.password = password
        self.active = True
        self.is_admin = False


    def get_id(self):
        return self.userName

    @property
    def is_active(self):
        return self.active



