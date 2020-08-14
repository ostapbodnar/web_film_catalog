from abc import ABC, abstractmethod
from flask import flash


# interface class for alert-classes
class Base_alert(ABC):

    @abstractmethod
    def alert(self, messeges):
        pass


# concrete realisation of alert class
# can be as default class for Decorator pattern notifing with(email, facebook)
class On_page_alert(Base_alert):

    def alert(self, messeges):
        for messege in messeges:
            flash(messege.messege, 'secondary')