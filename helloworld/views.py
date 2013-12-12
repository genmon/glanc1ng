from flask import render_template

from . import app
#from .forms import RegisterForm

@app.route("/")
@app.route("/index")
def index():
	return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated():
		return redirect(request.referrer or "/")
	
	#form = RegisterForm()
	
	return render_template('register.html')