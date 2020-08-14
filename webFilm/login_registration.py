from abc import ABC, abstractmethod
from flask_login import login_user
from webFilm import bcrypt, login_manager
from webFilm.dbClass import User, add_to_db
from flask import request, redirect


# this function is in charge of loading user from db
# it isn't used anywhere in code but is imortant for flask-loging
@login_manager.user_loader
def load_user_by_id(id):
    return User.query.get(int(id))


class IRegistration(ABC):

    @abstractmethod
    def validation_email(self, email):
        pass

    @abstractmethod
    def validation_password(self, password, confirm_password):
        pass

    @abstractmethod
    def register_check(self):
        pass

    @abstractmethod
    def register(self):
        pass


class Registration(IRegistration):

    # function that check if there already is email like this in db
    def validation_email(self, email):
        user = User.query.filter_by(email=email).first()
        if user:
            return True

        return False

    # matching two passwords (is used in registration route)
    def validation_password(self, password, confirm_password):
        return password != confirm_password

    def register_check(self):
        # getting info from form
        self.email = request.form['inputEmail']
        self.password = request.form['inputPassword']
        confirm_password = request.form['inputPassword2']

        # checking if this email is taken by another user
        taken = self.validation_email(self.email)

        # checking if password and confirmation password matches
        different = self.validation_password(self.password, confirm_password)

        if taken or different:
            return redirect("/registration", taken=taken, different=different)

    def register(self):

        # getting username from email ( all symbols to "@")
        username = self.email.split("@")

        # hashing password and converting it to string
        password_hash = bcrypt.generate_password_hash(
            self.password).decode('utf-8')

        user = User(username=username[0],
                    email=self.email,
                    password=password_hash)

        add_to_db(user)


class ILogin(ABC):

    @abstractmethod
    def login(self):
        pass


class Login(ILogin):

    def login_check(self):
        # getting all info from form on page "login.html"
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        self.remember_me = request.form.get('remember')

        # gettig user with that email
        self.user = User.query.filter_by(email=email).first()

        # cheking if there is user with that email and crypted passwords match
        return self.user and bcrypt.check_password_hash(self.user.password,
                                                        password)

    def login(self):

        login_user(self.user, remember=self.remember_me)

        return
