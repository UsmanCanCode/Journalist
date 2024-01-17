from flask import render_template, Blueprint, request
from flaskweb import db

bp = Blueprint('articles', __name__)


@bp.route('/articles/<author_id>/<author_name>')
def articles(author_id, author_name):
    twitter_url = request.args.get('twitter_profile')

    results = db.get_articles_by_id(author_id=author_id)

    return render_template('articles.html', author_name=author_name, author_id=author_id, articles=results,
                           twitter_profile=twitter_url)
