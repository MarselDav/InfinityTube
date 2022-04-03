import os

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def images_galery():
    videos = ["video/" + i for i in os.listdir("static/video")]
    # if request.method == "POST":
    #     file = request.files['file']
    #     image = Image.open(file)
    #     image.save("static/img/photo" + str(len(images) + 1) + ".png")
    if request.method == "POST":
        file = request.files["file"]
        file.save("static/video/" + str(len(videos) + 1) + ".mp4")

    return render_template("MainPage.html", videos=videos)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
