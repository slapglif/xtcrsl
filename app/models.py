from app import db_session,Base
from sqlalchemy import Column, Integer, String, Boolean, BLOB

## create db model class

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    steam_id = Column(String(40))
    nickname = Column(String(80))
    email = Column(String(80))


## set user in db
    @staticmethod
    def get_or_create(steam_id):
        rv = User.query.filter_by(steam_id=steam_id).first()
        if rv is None:
            rv = User()
            rv.steam_id = steam_id
            db_session.add(rv)
        return rv

## return python object as users nickname for easy access and display

    def __repr__(self):
        """docstring for __repr__"""
        return self.nickname

class Server(Base):
    __tablename__ = 'server'
    user_id = Column(Integer, primary_key=True)
    ip = Column(String())
    port = Column(String())
    type = Column(String())
    hostname = Column(String())
    map = Column(String())
    curplayers = Column(String())
    maxplayers = Column(String())


    @staticmethod
    def get_or_create(hostname):
        rv = Server.query.filter_by(hostname=hostname).first()
        if rv is None:
            rv = Server()
            rv.steam_id = hostname
            db_session.add(rv)
        return rv

    def __repr__(self):
        """docstring for __repr__"""
        return self.hostname