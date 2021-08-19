from flask import Flask
from flask import render_template
from flask import request
from .models import DB, User, Tweet
from .twitter import add_or_update_user
from .predict import predict_user
import os



def create_app():
    # get path to the pp directory
    app_dir = os.path.dirname(os.path.abspath(__file__))

    # Location of the database in the app directory
    database = "sqlite:///{}".format(os.path.join(app_dir, "twitoff.sqlite3"))

    app = Flask(__name__)

    # Setup database
    app.config['SQLALCHEMY_DATABASE_URI'] = database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    @app.route('/')
    def root():
        return render_template('layout_proto.html', title='Home', users = User.query.all())

    @app.route('/about')
    def about_me():
        return render_template('about.html')

    @app.route('/user', methods = ['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = f'User @{name} successfully added!'
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = f'Error adding @{name}: {e}'
            tweets = []
        return render_template('user.html', title = name, tweets=tweets, message=message)

    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        user0 = request.values['user0']
        user1 = request.values['user1']
        tweet_text = request.values['tweet_text']
        if user0 == user1:
            message = "Cannot compare a user to themself"
        else:
            prediction = predict_user(user0, user1, tweet_text)
            message = f'{tweet_text} is more likely to be said by @{user1 if prediction else user0} than @{user0 if prediction else user1}.'
        return render_template('predict.html', title='Prediction', message=message)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('layout_proto.html', title='Reset Database!')

    @app.route('/update')
    def update():
        update_all_users()
        return render_template('layout_proto.html', users=User.query.all(), title='All users and tweets updated!')


    @app.route('/delete')
    def delete_user():
        name = request.args['username']
        user_id = User.query.filter_by(name=name).first().id



        User.query.filter(User.name == name).delete()
        Tweet.query.filter(Tweet.user_id==user_id).delete()
        DB.session.commit()
        return render_template('layout_proto.html', users=User.query.all())

    return app



