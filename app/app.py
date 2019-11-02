from flask import Flask, render_template, request, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)


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
    var1 = 4
    return render_template("index.html", var=var1)



if __name__ == "__main__":
    app.run(debug=True)

