import datetime

import sqlalchemy
from flask_login import UserMixin

import data.db_session as db_session
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    channel_description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    channel_country = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    mail_for_cooperation = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    vk = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    inst = sqlalchemy.Column(sqlalchemy.String, nullable=True)
