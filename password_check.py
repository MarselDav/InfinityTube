import bcrypt

import data.db_session as db_session
from data.users import User


def hashing(string):  # хэширование пароля
    return bcrypt.hashpw(string.encode(), bcrypt.gensalt()).decode()


def comparison(string, hash_string):  # сравнение пароля с захэшированым
    return bcrypt.checkpw(string.encode(), hash_string)


def check_password(email, password):  # сравнить пароль с паролем от этого аккаунта
    db_sess = db_session.create_session()
    hashed_password = db_sess.query(User).filter(User.email == email).first().hashed_password.encode()
    return comparison(password, hashed_password)


def password_strength_check(password):  # проверка надежности пароля
    if len(password) < 8 or len(password) >= 16:
        return False, "Пароль должен содержать больше 12 символов, но меньше 16"
    if password.lower() == password:
        return False, "Пароль должен содержать заглавные и прописные буквы"
    return True, ""
