from webFilm import db
from flask_login import UserMixin
import dependency_injector.containers as containers
import dependency_injector.providers as providers
from flask import request
from webFilm.base_alert import Base_alert


# db table
# sqlalchemy many to many relsationship (many masseges for many users)
messege_table = db.Table('messege_table',
                         db.Column('messege_id', db.Integer,
                                   db.ForeignKey('messege.id')),
                         db.Column('user_id', db.Integer,
                                   db.ForeignKey('user.id')))


# db.Model inherinatce is for adding this class to databade site.db
# all messeges are stored in database as instance of this class
class Messege(db.Model):
    __tablename__ = 'messege'

    id = db.Column(db.Integer, primary_key=True)
    messege = db.Column(db.String(120), nullable=False)

    # relatinship with class User ( this class is used in messege_table )
    users = db.relationship('User', secondary=messege_table,
                            back_populates="messeges")


# db.Model inherinatce is for adding this class to databade site.db
class Film(db.Model):
    __tablename__ = 'film'

    # fileds that is representing info about films
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    release_date = db.Column(db.String(10), nullable=False)
    runtime = db.Column(db.Integer, nullable=True)
    director = db.Column(db.String(20), nullable=False)
    actors = db.Column(db.String(80), nullable=False)
    budget = db.Column(db.Integer, nullable=True)
    cross_world = db.Column(db.Integer, nullable=True)

    trailer_url = db.Column(db.String(80))

    storyline = db.Column(db.Text, nullable=False)

    img_url = db.Column(db.String(80))

    # db ForeignKey/ user reference
    # this relathanship is used as wishlist realisation
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Film('{self.name}', '{self.director}', '{self.release_date}')"

    def get_film(id):
        return Film.query.get_or_404(id)

    def add_new_film():
        new_film = Film()
        new_film.update()
        return add_to_db(new_film)

    def update(self):
        self.img_url = request.form['film_image']

        self.name = request.form['film_name']
        self.rate = request.form['film_rate']
        self.release_date = request.form['film_release_date']
        self.runtime = request.form['film_runtime']
        self.director = request.form['film_director']
        self.actors = request.form['film_actors']
        self.budget = request.form['film_budget']
        self.cross_world = request.form['film_cross_world']

        self.trailer_url = request.form['film_trailer_url']

        self.storyline = request.form['film_storyline']

        try:
            db.session.commit()
        except Exception:
            return "ERROR"


# UserMixin is parent class aimed to make registation and validation avaliable
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(40), nullable=False)

    wishlist_films = db.relationship('Film',
                                     backref=db.backref('wishlist_films',
                                                        lazy=True))

    # field that indicate if user is subscriber or not
    subscriber = db.Column(db.Boolean, default=False)

    # relathanship to messege_table
    # all messegs are represent as list in this variable
    messeges = db.relationship('Messege', secondary=messege_table,
                               back_populates="users")

    def __repr__(self):
        return f"User, email: {self.email}"

    # function that sends messeges to user when he is loading homepage
    def sendMessege(self, type_of_notifying: Base_alert):

        if len(self.messeges) > 0:

            type_of_notifying.alert(self.messeges)

            self.messeges = []
            db.session.commit()


class Wishlist():

    def __init__(self, user):
        self.user = user

    def get_wishlist(self):
        return self.user.wishlist_films

    def add_to_user_wishlist(self, id):
        film = Film.get_film(id)
        self.user.wishlist_films.append(film)
        db.session.commit()

    def delete_from_user_wishlist(self, id):
        film = Film.get_film(id)
        self.user.wishlist_films.remove(film)
        db.session.commit()


# adding obj to database "site.db"
def add_to_db(obj):
    try:
        db.session.add(obj)
        db.session.commit()
        return obj
    except Exception:
        return "Error!"


# deleting obj from db "site.db"
def delete_from_db(obj):
    try:
        db.session.delete(obj)
        db.session.commit()
    except Exception:
        return "Error!"


# IoC container for film class
class FilmFactory(containers.DeclarativeContainer):
    film = providers.Factory(Film)


