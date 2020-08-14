from webFilm import app
from flask import render_template, request, url_for, redirect, flash
from webFilm.dbClass import Film, User, delete_from_db, Wishlist
from webFilm.observer import ObserverSingleton
from webFilm.base_alert import On_page_alert
from webFilm.login_registration import Registration, Login
from flask_login import current_user, logout_user


# observer's task - notify veretified user

observer = ObserverSingleton.observer()


# routes to homepage
@app.route("/")
@app.route("/home")
def home():

    # getting all film from Database

    films = Film.query.order_by(Film.id).all()
    global wishlists
    wishlists = Wishlist(current_user)

    # sending possible flash messeges to page "home.html" if user is loged in

    if current_user.is_authenticated:
        base_flash_notifyer = On_page_alert()
        current_user.sendMessege(base_flash_notifyer)

    return render_template("home.html", films=films)


# adding new film
@app.route("/new_film", methods=['GET', 'POST'])
def new_film():
    if request.method == 'POST':

        # reading info from form in "new_film.html"
        new_film = Film.add_new_film()

        # notifing subscribed isers about adding new film
        observer.notify(f'Film "{new_film.name}" was added!')

        return render_template('film.html', film=new_film)

    else:
        return render_template("new_film.html")


# routes to page with film  that id

@app.route("/film/<int:id>", methods=['GET', 'POST'])
def film(id):
    film = Film.get_film(id)
    return render_template("film.html", film=film)


# route to delete film with that id
@app.route("/film_delete/<int:id>")
def film_delete(id):
    if current_user.is_authenticated:
        film = Film.get_film(id)

        delete_from_db(film)

        # notifing about deleting film
        observer.notify(f'Film "{film.name}" was deleted!')

        return redirect('/')

    flash("You have no permission for that!")
    return redirect('/')


# route to update info about film
# if method POSt then this function udpate info
# in another case it opens page for entering info
@app.route("/film_update/<int:id>", methods=['GET', 'POST'])
def film_update(id):
    film = Film.get_film(id)
    if request.method == 'POST':

        # getting info for update from form on page "film_update.html"
        film.update()
        # redirectig user to updated film
        return render_template("film.html", film=film)

    else:
        return render_template("film_update.html", film=film)


# route to registetion form (" registration.html ")
@app.route("/registration", methods=['GET', 'POST'])
def registration():
    # checking if user is alresdy logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == "POST":

        registration_user = Registration()
        registration_user.register_check()
        registration_user.register()

        return render_template('login.html')

    return render_template("registration.html")


# login function
@app.route("/login", methods=['GET', 'POST'])
def login(nextpage="home"):
    # nextpage argument is used for redirecting user to that page after logging

    # check if user is already loged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == "POST":

        login = Login()

        if login.login_check():
            login.login()
            
            return redirect(f'/{nextpage}')
        else:

            # alerting user that there was wrong password or email
            flash('Login Unsuccessful. Please check email and password',
                  'danger')

    return render_template("login.html")


# logout function
# using logout_user() from flask-login
@app.route("/logout")
def logout():
    logout_user()
    return redirect('/home')


@app.route("/user_delete/<int:id>")
def user_delete(id):
    if current_user.is_authenticated:

        logout_user()

    user = User.query.get_or_404(id)

    delete_from_db(user)

    return redirect('/')


# route to user's wishlist
@app.route("/wishlist")
def wishlist():
    # cheking if user is logged in if not  redirecting to loggin pahe
    if not current_user.is_authenticated:
        return render_template("login.html", nextpage='wishlist')

    global wishlists
    films = wishlists.get_wishlist()
    return render_template("wishlist.html", films=films)


# adding film to wishlist
@app.route("/wishlist/add/<int:id>")
def add_film_to_wishlist(id):

    if not current_user.is_authenticated:
        return render_template("login.html", nextpage='wishlist/add/<int:id>')

    global wishlists
    wishlists.add_to_user_wishlist(id)
    return redirect(f'/film/{id}')


# deleting film from user's wishlist
@app.route("/wishlist/detele/<int:id>")
def wishlist_film_delete(id):

    global wishlists
    wishlists.delete_from_user_wishlist(id)

    return redirect(f'/film/{id}')


# subscribing user on webpage news( adding/deleting films)
@app.route("/subscribe")
def subscribe():

    if not current_user.is_authenticated:
        return render_template("login.html", nextpage=f'subscribers/add/{id}')

    observer.subscribe(current_user)

    return redirect(url_for('home'))


# removing subscribe on webpage news
@app.route("/remove_subscribe")
def remove_subscribe():

    if not current_user.is_authenticated:
        return render_template("login.html", nextpage=f'subscribers/add/{id}')

    observer.unsubscribe(current_user)

    return redirect(url_for('home'))
