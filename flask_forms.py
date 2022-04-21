from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import PasswordField, BooleanField, SubmitField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class UploadVideoForm(FlaskForm):
    videofile = FileField("Выберите видео")
    video_name = StringField('Название видео', validators=[DataRequired()])
    description = TextAreaField("Описание видео")
    submit = SubmitField("Подтвердить")


class ChannelSettings(FlaskForm):
    channel_name = StringField("Название канала", default="", validators=[DataRequired()])

    #  Дополнительная информация #
    country = StringField("Страна")
    mail_for_cooperation = StringField("email для сотрудничества", validators=None)

    vk = StringField("vk")
    inst = StringField("instagram")

    submit = SubmitField("Подтвердить")