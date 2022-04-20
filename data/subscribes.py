import sqlalchemy
from flask_login import UserMixin

import data.db_session as db_session
from .db_session import SqlAlchemyBase


class PeopleSubscribes(SqlAlchemyBase, UserMixin):
    __tablename__ = "peoplesubscribes"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    person_id = sqlalchemy.Column(sqlalchemy.Integer)
    channel_id = sqlalchemy.Column(sqlalchemy.Integer)
