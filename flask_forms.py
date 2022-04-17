from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import PasswordField, BooleanField, SubmitField, StringField, TextAreaField, RadioField
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
    # choose_preview = RadioField('Выберите иконку видео',
    #                             choices=[('image1', ""), ('image2', ""), ('image2', "")])
    submit = SubmitField("Подтвердить")


class ChoosePreviewForm(FlaskForm):
    videofile = FileField("Выберите видео")
    # choose_preview = RadioField('Выберите иконку видео',
    #                             choices=[('image1', ""), ('image2', ""), ('image2', "")])
    submit = SubmitField("Подтвердить")