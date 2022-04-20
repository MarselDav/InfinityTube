import datetime

import sqlalchemy

import data.db_session as db_session
from .db_session import SqlAlchemyBase


class OpenAccessVideos(SqlAlchemyBase):
    __tablename__ = "openaccessvideos"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    saving_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    videoname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_data = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    preview_image = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    likes_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    dislikes_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    watches = sqlalchemy.Column(sqlalchemy.Integer, default=0)
