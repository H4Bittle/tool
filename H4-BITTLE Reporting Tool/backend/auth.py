import json
import bcrypt
import os

USERS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'users.json')

class User:
    def __init__(self, username, password):
        self.id = username
        self.username = username
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

def load_user(username):
    if not os.path.exists(USERS_FILE):
        return None
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    return users.get(username)

def authenticate(username, password):
    user = load_user(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return True
    return False
