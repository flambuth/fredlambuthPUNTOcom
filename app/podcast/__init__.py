from flask import Blueprint

bp = Blueprint('podcast', __name__)

from app.podcast import routes