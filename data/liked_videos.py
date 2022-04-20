import sqlalchemy
from flask_login import UserMixin

import data.db_session as db_session
from .db_session import SqlAlchemyBase


class LikedVideos(SqlAlchemyBase, UserMixin):
    __tablename__ = "likedvideos"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    video_id = sqlalchemy.Column(sqlalchemy.Integer)
    person_id = sqlalchemy.Column(sqlalchemy.Integer)
    reaction = sqlalchemy.Column(sqlalchemy.VARCHAR, default="none")