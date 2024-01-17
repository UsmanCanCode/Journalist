from flask import render_template, Blueprint
from flaskweb import db

bp = Blueprint('authors', __name__)


@bp.route('/authors')
def authors():
    results = db.get_authors()

    return render_template('authors.html', title='Authors', authors=results)
