from webFilm import db
from webFilm.dbClass import Messege, User
import dependency_injector.containers as containers
import dependency_injector.providers as providers


#function that controls max size of messeges in database
def delete_old_messege(size=10):
    table_size = db.session.query(Messege).count()
    if table_size > size:
        messege_to_delete = Messege.query.order_by(Messege.id).first()

        db.session.delete(messege_to_delete)


# realisation of Observer Pattern
class Observer():

    # subscribing current user on webpage updates
    def subscribe(self, current_user):
        current_user.subscriber = True
        db.session.commit()

    #  removing subscribe
    def unsubscribe(self, current_user):
        current_user.subscriber = False
        db.session.commit()

    # function for notifying all subscribed users when home page is opened
    def notify(self, event):

        users = User.query.filter_by(subscriber=True)
        messege = Messege(messege=event)

        db.session.add(messege)
        delete_old_messege()

        for user in users:
            user.messeges.append(messege)

        db.session.commit()


# using containers.DeclarativeContainer as IOC-container realisation
# using Singleton pattern for creating only one possible Observer instance
class ObserverSingleton(containers.DeclarativeContainer):
    observer = providers.Singleton(Observer)
