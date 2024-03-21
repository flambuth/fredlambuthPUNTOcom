from flask import Blueprint

bp = Blueprint('user_accounts', __name__)

from app.user_accounts import routes