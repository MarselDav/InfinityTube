import os

from PIL import Image
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def images_galery():
    images = ["img/" + i for i in os.listdir("static/img")[1::]]
    if request.method == "POST":
        file = request.files['file']
        image = Image.open(file)
        image.save("static/img/photo" + str(len(images) + 1) + ".png")
    return render_template("index.html", images=images, len_=(len(images) + 1))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
