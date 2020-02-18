from flask import Flask, render_template, request, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import webbrowser

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'dev'

db = SQLAlchemy(app)

class BasicObj():

    def __init__(self, name=None):
        self.name = name


class RelApp(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Task {0}>".format(self.id)


@app.route("/", methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        pass
    else:
        pass
    obj = BasicObj("test1")
    return render_template("index.html", obj=obj)



if __name__ == "__main__":
    app.run(debug=True)
    webbrowser.open_new("127.0.0.1:5000")

