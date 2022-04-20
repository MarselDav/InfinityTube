import sqlalchemy
from flask_login import UserMixin

import data.db_session as db_session
from .db_session import SqlAlchemyBase


class Comments(SqlAlchemyBase, UserMixin):
    __tablename__ = "comments"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    video_id = sqlalchemy.Column(sqlalchemy.Integer)
    person_id = sqlalchemy.Column(sqlalchemy.Integer)
    comment = sqlalchemy.Column(sqlalchemy.Text)