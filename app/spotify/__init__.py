from flask import Blueprint
from app.spotify.cache import cache

bp = Blueprint('spotify', __name__)

from app.spotify import routes