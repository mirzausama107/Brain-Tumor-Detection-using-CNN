from flask import Flask, render_template, request, url_for, redirect
import os
from click import File

from brain_tumor_detection import hello

app = Flask(__name__)
app.secret_key = os.urandom(24)
project_dir = os.path.abspath(os.path.dirname(__file__))

# print(project_dir)
print("=" * 100)


# database_file = "sqlite:///{}".format(os.path.join(project_dir, "book.db"))
# app.config["SQLALCHEMY_DATABASE_URI"] = database_file
# db = SQLAlchemy(myApp)


@app.route("/")
def run():
    return render_template("index.html")

@app.route("/message", methods=['GET', 'POST'])
def message():
    target_path = os.path.join(project_dir, 'static/images')
    if not os.path.isdir(target_path):
        os.mkdir(target_path)
    if request.method == 'POST':
        Pic = request.files["abc"]
        image = Pic.filename
        destination = "/".join([target_path, image])
        Pic.save(destination)
        hello(image)

        return render_template("images.html",image=image)
    return "v"



if __name__ == '__main__':
    app.run(debug=True)
