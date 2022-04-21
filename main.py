import os
from waitress import serve

from flask import Flask, render_template, request, make_response, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.comments import Comments
from data.liked_videos import LikedVideos
from data.subscribes import PeopleSubscribes
from data.users import User
from data.videos import OpenAccessVideos
from flask_forms import LoginForm, UploadVideoForm, ChannelSettings
from password_check import hashing, check_password, password_strength_check
from uniq_filename import get_uniq_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPER_PUPER_MEGA_SECRET_KEY'

login_manager = LoginManager()
login_manager.init_app(app)

videos = []


@app.route("/", methods=["POST", "GET"])  # главная страница
def mainpage():
    global videos

    if not os.path.isdir("static/video"):
        os.mkdir("static/video")

    db_sess = db_session.create_session()
    videos = []
    if current_user.is_authenticated:
        for i in os.listdir("static/video"):
            try:
                videoinfo = db_sess.query(OpenAccessVideos).filter(OpenAccessVideos.saving_name == i).first()
                videoname = videoinfo.videoname
                channel_id = videoinfo.author_id
                channel_name = db_sess.query(User).filter(User.id == channel_id).first().name
                videos.append([i, videoname, channel_name, channel_id])
            except AttributeError:
                print("Отсутствует атрибут")

    return render_template("MainPage.html", videos=videos)


@app.route("/open_video/<videofilename>", methods=["POST", "GET"])  # открыть какое-либо видео в отдельном окне
def open_video(videofilename):
    print("current_user:", current_user.id)
    db_sess = db_session.create_session()
    video_information = db_sess.query(OpenAccessVideos).filter(OpenAccessVideos.saving_name == videofilename).first()
    user_info = db_sess.query(User).filter(User.id == video_information.author_id).first()
    channel = user_info.name
    channel_id = user_info.id
    videoid = video_information.id
    print("id:", videoid)

    likes_count, dislikes_count = get_likes_and_dislikes_count(videoid)

    liked_info = db_sess.query(LikedVideos).filter(
        (LikedVideos.video_id == videoid), (LikedVideos.person_id == current_user.id)).first()
    if not liked_info:
        reaction = "none"
    else:
        reaction = liked_info.reaction

    if reaction == "like":
        like_color = "red"
        dislike_color = "blue"
    elif reaction == "dislike":
        like_color = "blue"
        dislike_color = "red"
    else:
        like_color = "blue"
        dislike_color = "blue"

    subscribe_status = db_sess.query(PeopleSubscribes).filter(
        (PeopleSubscribes.channel_id == channel_id), (PeopleSubscribes.person_id == current_user.id))
    if not subscribe_status.first():
        subscribe_button_color = "red"
        subscribe_button_text = "Подписаться"
    else:
        subscribe_button_color = "grey"
        subscribe_button_text = "Вы подписаны"

    video_info = {
        "name": videofilename,
        "videoname": video_information.videoname,
        "channel": channel,
        "channel_id": channel_id,
        "description": video_information.description,
        "likes_count": likes_count,
        "dislikes_count": dislikes_count
    }

    if request.method == "POST":
        reaction_on_video = request.form["reaction"]
        if reaction_on_video in ["Нравится", "Не нравится"]:
            set_like(reaction_on_video, videoid, current_user.id, reaction)
        elif reaction_on_video == "Отправить":
            comment_text = request.form["comment"]
            add_new_comment(videoid, current_user.id, comment_text)
        else:
            if channel_id != current_user.id:
                if subscribe_button_text == "Вы подписаны":
                    subscribe_status.delete()
                    db_sess.commit()
                else:
                    set_subscribe(channel_id, current_user.id)

        return redirect(f"/open_video/{videofilename}")

    all_comments_info = db_sess.query(Comments).filter(Comments.video_id == videoid).all()
    comments = []
    if all_comments_info:
        for comment_info in all_comments_info:
            person_info = db_sess.query(User).filter(User.id == comment_info.person_id).first()
            comments.append([person_info.name, comment_info.person_id, comment_info.comment])
    return render_template("Open_video.html", video_info=video_info, like_color=like_color,
                           subscribe_button_color=subscribe_button_color, subscribe_button_text=subscribe_button_text,
                           dislike_color=dislike_color, comments=comments)


@app.route("/subscribes_channels")  # открыть списко подписок
def subscribes_channels():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()

        channel_list = []
        channels_info = db_sess.query(PeopleSubscribes).filter(PeopleSubscribes.person_id == current_user.id).all()
        for channel in channels_info:
            channel_id = channel.channel_id
            user_name = db_sess.query(User).filter(User.id == channel_id).first().name
            channel_list.append([channel_id, user_name])
        return render_template("Subscribes_channels.html", channel_list=channel_list)
    else:
        return "Вы не авторизованы"


def get_likes_and_dislikes_count(videoid):  # получить кол-во лайков и дизлайков
    db_sess = db_session.create_session()
    video = db_sess.query(OpenAccessVideos).filter(OpenAccessVideos.id == videoid).first()
    likes_count = video.likes_count
    dislikes_count = video.dislikes_count
    return likes_count, dislikes_count


def set_like(reaction_on_video, videoid, person_id, reaction):  # поставить лайк или дизлайк на видео
    print(videoid)
    likes_count, dislikes_count = get_likes_and_dislikes_count(videoid)

    db_sess = db_session.create_session()
    video = db_sess.query(OpenAccessVideos).filter(OpenAccessVideos.id == videoid).first()
    liked_info = db_sess.query(LikedVideos).filter(
        (LikedVideos.person_id == current_user.id), (LikedVideos.video_id == videoid)).first()
    if not liked_info:
        print("add like")
        liked_videos = LikedVideos()
        liked_videos.video_id = videoid
        liked_videos.person_id = current_user.id
        liked_videos.reaction = "none"
        db_sess.add(liked_videos)
        db_sess.commit()
        liked_info = db_sess.query(LikedVideos).filter(
            (LikedVideos.person_id == current_user.id), (LikedVideos.video_id == videoid)).first()
    if reaction_on_video == "Нравится":
        if reaction == "like":
            video.likes_count = likes_count - 1
            liked_info.reaction = "none"
        else:
            video.likes_count = likes_count + 1
            liked_info.reaction = "like"
            if reaction == "dislike":
                video.dislikes_count = dislikes_count - 1
    else:
        if reaction == "dislike":
            video.dislikes_count = dislikes_count - 1
            liked_info.reaction = "none"
        else:
            video.dislikes_count = dislikes_count + 1
            liked_info.reaction = "dislike"
            if reaction == "like":
                video.likes_count = likes_count - 1
    db_sess.commit()


def set_subscribe(channel_id, user_id):  # подписаться на канал
    db_sess = db_session.create_session()

    subscribes = PeopleSubscribes()
    subscribes.person_id = user_id
    subscribes.channel_id = channel_id

    db_sess.add(subscribes)
    db_sess.commit()


@login_manager.user_loader
def load_user(user_id):  # авторизироваться
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/logout")
@login_required
def logout():  # выйти из аккаунта
    logout_user()
    return redirect("/")


@app.route("/login", defaults={"email": ""}, methods=["GET", "POST"])
@app.route("/login/<email>", methods=["GET", "POST"])
def login(email):  # залогиниться на сайте
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and check_password(form.email.data, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template("Logged_page.html", message="Неправильный логин или пароль", form=form, email=email)

    return render_template("Logged_page.html", form=form, email=email)


@app.route("/signinchooser", methods=["POST", "GET"])  # страница выбора аккаунтов
def sign_in_chooser():
    accounts = []
    for acc in ["account1", "account2", "account3"]:
        cookie = request.cookies.get(acc)
        if cookie:
            accounts.append(cookie)

    return render_template("Signinchooser.html", accounts=accounts)


@app.route("/registration", methods=["POST", "GET"])  # страница с формой регистрации
def registration():
    email_message = ""
    confirm_password_message = ""

    res = make_response(render_template("Registration.html", email_message=email_message,
                                        confirm_password_message=confirm_password_message))
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if presence(email):  # проверка на существование email
            email_message = "Такой адресс уже зарегистрирован"

        if email == "":
            email_message = "Вы не ввели email"

        if password != request.form["confirm_password"]:
            confirm_password_message = "Пароли не соответсвуют"

        check = password_strength_check(password)
        if not check[0]:
            confirm_password_message = check[1]

        res = make_response(render_template("Registration.html", email_message=email_message,
                                            confirm_password_message=confirm_password_message))
        if email_message + confirm_password_message == "":
            add_new_user(username, email, password)
            for acc in ["account1", "account2", "account3"]:
                if not request.cookies.get(acc):
                    res.set_cookie(acc, email)
                    break

    return res


@app.route("/channel/<channel_id>/featured", methods=["POST", "GET"])
def channel_mainpage(channel_id):  # открыть главную страницу канала
    global videos

    db_sess = db_session.create_session()
    if request.method == "POST":
        print("Подписаться")
    user_info = db_sess.query(User).filter(User.id == channel_id).first()
    channel_name = user_info.name

    this_author_videos = []
    for videoinfo in db_sess.query(OpenAccessVideos).filter(OpenAccessVideos.author_id == channel_id).all():
        videoname = videoinfo.videoname
        saving_name = videoinfo.saving_name
        this_author_videos.append([saving_name, videoname])

    active_buttons_classes = ["nav-item nav-link active", "nav-item nav-link", "nav-item nav-link"]

    return render_template("Channel_featured.html", this_author_videos=this_author_videos, channel_id=int(channel_id),
                           channel_name=channel_name, active_buttons_classes=active_buttons_classes)


@app.route("/channel/<channel_id>/channel_description", methods=["POST", "GET"])
def channel_description(channel_id):  # открыть описание канала
    db_sess = db_session.create_session()
    if request.method == "POST":
        pass
    user_info = db_sess.query(User).filter(User.id == channel_id).first()
    channel_name = user_info.name
    description = user_info.channel_description
    channel_country = user_info.channel_country
    if not channel_country:
        channel_country = "Не указано"

    mail_for_cooperation = user_info.mail_for_cooperation
    vk = user_info.vk
    inst = user_info.inst

    if not description:
        description = "Описание канала не указано"

    active_buttons_classes = ["nav-item nav-link", "nav-item nav-link", "nav-item nav-link active"]

    return render_template("Channel_description.html", description=description, channel_id=int(channel_id),
                           channel_name=channel_name, active_buttons_classes=active_buttons_classes,
                           channel_country=channel_country, vk=vk, inst=inst, mail_for_cooperation=mail_for_cooperation)


@app.route("/channel_settings/<channel_id>", methods=["POST", "GET"])
def channel_settings(channel_id):  # настройки канала
    form = ChannelSettings()
    if current_user.is_authenticated:
        if current_user.id == int(channel_id):
            db_sess = db_session.create_session()
            channel_info = db_sess.query(User).filter(User.id == channel_id).first()

            default_settings = {
                "name": channel_info.name if channel_info.name is not None else "",
                "description": channel_info.channel_description if channel_info.channel_description is not None else "",
                "country": channel_info.channel_country if channel_info.channel_country is not None else "",
                "mail": channel_info.mail_for_cooperation if channel_info.mail_for_cooperation is not None else "",
                "vk": channel_info.vk if channel_info.vk is not None else "",
                "inst": channel_info.inst if channel_info.inst is not None else "",
            }

            if form.validate_on_submit():
                channel_name = form.channel_name.data
                channel_description = request.form["channel_description"]
                channel_country = form.country.data
                mail_for_cooperation = form.mail_for_cooperation.data
                vk = form.vk.data
                inst = form.inst.data
                set_chanel_settings(channel_name, channel_id, channel_description, channel_country,
                                    mail_for_cooperation, vk, inst)
                return redirect(f"/channel/{channel_id}/featured")

            return render_template("Channel_settings.html", form=form, default_settings=default_settings)
        return "У вас нет доступа"
    return "Авторизуйтесь"


@app.route("/upload_video", methods=["POST", "GET"])
def set_video_info():  # загрузить видео
    form = UploadVideoForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        saving_name = get_uniq_filename()
        form.videofile.data.save("static/video/" + saving_name)

        user_id = current_user.id
        videoname = form.video_name.data
        description = form.description.data

        add_new_video(saving_name, videoname, description, user_id)

        return redirect("/")

    return render_template("Video_info.html", form=form)


def get_info_for_email(user_email):  # получить информацию о пользователе по email
    db_sess = db_session.create_session()
    info = db_sess.query(User).filter(User.email == user_email).first()
    return info


def presence(user_email):  # наличие email в бд
    info = get_info_for_email(user_email)
    if not info:
        return info
    return info.email


def get_user_password(user_email):  # получить пароль пользователя
    info = get_info_for_email(user_email)
    if not info:
        return info
    return info.hashed_password


def add_new_user(username, email, password):  # добавить нового пользователя
    user = User()
    user.name = username
    user.email = email
    user.hashed_password = hashing(password)

    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()

    user = db_sess.query(User).filter(User.email == email).first()
    login_user(user)


def add_new_video(saving_name, videoname, description, userid):  # добавить новое видео
    video = OpenAccessVideos()
    video.videoname = videoname
    video.saving_name = saving_name
    video.author_id = userid
    video.description = description

    db_sess = db_session.create_session()
    db_sess.add(video)
    db_sess.commit()


def add_new_comment(videoid, personid, comment_text):  # добавить комментарий к видео
    comm = Comments()
    comm.video_id = videoid
    comm.person_id = personid
    comm.comment = comment_text

    db_sess = db_session.create_session()
    db_sess.add(comm)
    db_sess.commit()


def set_chanel_settings(channel_name, channel_id, description, country, mail, vk, inst):  # установить настройки канала
    db_sess = db_session.create_session()

    channel = db_sess.query(User).filter(User.id == channel_id).first()
    channel.name = channel_name
    channel.channel_description = description
    channel.channel_country = country
    channel.mail_for_cooperation = mail
    channel.vk = vk
    channel.inst = inst
    db_sess.commit()


def main():  # главная функция
    db_session.global_init("db/database.db")
    port = int(os.environ.get("PORT", 5000))
    serve(app, host='0.0.0.0', port=port)
    # app.run(host='0.0.0.0', port=port)
    # app.run(host="127.0.0.1", port=5000)


if __name__ == '__main__':
    main()
