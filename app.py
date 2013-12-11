import os
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

# initialization
app = Flask(__name__)
app.config.update(
	DEBUG = True,
	#SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'],
)

db = SQLAlchemy(app)

# controllers
@app.route("/")
def hello():
	return render_template("index.html")

# launch
if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)
