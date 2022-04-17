import bcrypt

import data.db_session as db_session
from data.users import User


def hashing(string):
    return bcrypt.hashpw(string.encode(), bcrypt.gensalt()).decode()


def comparison(string, hash_string):
    return bcrypt.checkpw(string.encode(), hash_string)


# def check_password(password):
#     db_sess = db_session.create_session()
#     print(hashing(password))
#     return db_sess.query(User).filter(User.hashed_password == hashing(password))

def check_password(email, password):
    db_sess = db_session.create_session()
    hashed_password = db_sess.query(User).filter(User.email == email).first().hashed_password.encode()
    return comparison(password, hashed_password)

# print(comparison("1234", "$2b$12$8YHlj/qDpNWOJCRstRSXWOgvRbL1yKaxcertvGJ39.ns63y.m1Fc.".encode()))

