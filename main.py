import os

from flask import Flask, render_template, request, make_response, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from uniq_filename import get_uniq_filename
from data import db_session
from data.users import User
from data.videos import OpenAccessVideos
from flask_forms import LoginForm, UploadVideoForm
from get_video_preview import get_standart_preview
from password_check import hashing, check_password
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'DLICNY__R*V8NYJDIULUdh63t81cu8DT22872T'

login_manager = LoginManager()
login_manager.init_app(app)

videos = []


@app.route("/", methods=["POST", "GET"])
def mainpage():
    global videos

    videos = [i for i in os.listdir("static/video")]

    return render_template("MainPage.html", videos=videos)


@app.route("/open_video/<videofilename>", methods=["POST", "GET"])
def open_video(videofilename):
    videofilename = videofilename

    return render_template("Open_video.html", name=videofilename)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/login", defaults={"email": ""}, methods=["GET", "POST"])
@app.route("/login/<email>", methods=["GET", "POST"])
def login(email):
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and check_password(form.email.data, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template("Logged_page.html", message="Неправильный логин или пароль", form=form, email=email)

    return render_template("Logged_page.html", form=form, email=email)


@app.route("/signinchooser", methods=["POST", "GET"])
def sign_in_chooser():
    accounts = []
    if request.cookies.get("accounts"):
        account = request.cookies.get("accounts")
        accounts.append(account)

    return render_template("Signinchooser.html", accounts=accounts)


@app.route("/registration", methods=["POST", "GET"])
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

        res = make_response(render_template("Registration.html", email_message=email_message,
                                            confirm_password_message=confirm_password_message))
        if email_message + confirm_password_message == "":
            add_new_user(username, email, password)
            res.set_cookie("accounts", email)

    return res


# @app.route("/upload_video", methods=["POST", "GET"])
# def upload_video():
#     global videos
#     if request.method == "POST":
#         db_sess = db_session.create_session()
#         file = request.files["video"]
#         videoname = str(db_sess.query(OpenAccessVideos).count() + 1) + ".mp4"
#         file.save("static/video/" + videoname)
#         get_standart_preview(videoname)
#
#         # return redirect("/video_info")
#
#     return render_template("Upload_video.html")


@app.route("/upload_video", methods=["POST", "GET"])
def set_video_info():
    form = UploadVideoForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        saving_name = get_uniq_filename()
        form.videofile.data.save("static/video/" + saving_name)
        get_standart_preview(saving_name)

        user_id = current_user.id
        videoname = form.video_name.data
        description = form.description.data
        # print(user_id, videofile, videoname, description)
        # return f"{user_id} {videofile} {videoname} {description}"

        add_new_video(saving_name, videoname, description, user_id)

        return redirect(f"/choose_preview/{saving_name}")

    return render_template("Video_info.html", form=form)


@app.route("/choose_preview/<videoname>", methods=["POST", "GET"])
def choose_video_preview(videoname):
    form = UploadVideoForm()
    if form.validate_on_submit():
        pass

    return render_template("Choose_preview.html", form=form)


def get_info_for_email(user_email):
    db_sess = db_session.create_session()
    info = db_sess.query(User).filter(User.email == user_email).first()
    return info


def presence(user_email):
    info = get_info_for_email(user_email)
    if not info:
        return info
    return info.email


def get_user_password(user_email):
    info = get_info_for_email(user_email)
    if not info:
        return info
    return info.hashed_password


def add_new_user(username, email, password):
    user = User()
    user.name = username
    user.email = email
    user.hashed_password = hashing(password)

    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()


def add_new_video(saving_name, videoname, description, userid):
    video = OpenAccessVideos()
    video.videoname = videoname
    video.saving_name = saving_name
    video.author_id = userid
    video.description = description

    db_sess = db_session.create_session()
    db_sess.add(video)
    db_sess.commit()


def main():
    db_session.global_init("db/database.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
