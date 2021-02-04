from app import app

from flask import render_template, request, redirect, jsonify, make_response

from datetime import datetime

import os

from werkzeug.utils import secure_filename

@app.template_filter('clean_date')
def clean_date(dt):
	return dt.strftime('%d %b %Y')

@app.route('/')
def index():
	print(app.config["DB_NAME"])
	return render_template('public/index.html')

@app.route('/jinja')
def jinja():
	my_name = 'Vu Ngoc Vinh'
	age = 25
	langs = ["Python", "c", "c#", "java", "Erlang",]
	friends = {
		"Tom": 30,
		"Amy": 25
	}
	cool = True
	colours = ('red', 'green')

	class GitRemote:
		def __init__(self, name, description, url):
			self.name = name
			self.description = description
			self.url = url

		def pull(self):
			return f"Pullin repo {self.name}"

		def clone(self):
			return f"Cloning into {self.url}"

	my_remote = GitRemote(
		name='flask Jinja',
		description='template design tutorial',
		url='https://github.com/julian-nash/jinja.git',
	) 

	def repeat(x, qty):
		return x * qty

	date = datetime.utcnow()

	my_html = '<h1>This is some html</h1>'

	suspicious = '<script>alert("YOU GOT HACKED")</script>'

	return render_template('public/jinja.html', my_name=my_name, langs=langs,
	friends=friends, age=age, colours=colours, cool=cool, GitRemote=GitRemote, 
	repeat=repeat, my_remote=my_remote, date=date, my_html=my_html,
	suspicious=suspicious)

@app.route('/about')
def about():
	return "<h1 style='color: red'>About!!!</h1>"

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():

	if request.method == "POST":
		req = request.form
		username = req["username"]
		email = req.get("email")
		password = request.form["password"]
		print(username, email, password)
		return redirect(request.url)
	return render_template('public/sign_up.html')

users = {
	"vinh": {
		"name": "vu ngoc vinh",
		"bio": "Awesomes",
		"facebook": "@vungocvinh95",
	},
	"elonmusk": {
		"name": "Elon Musk",
		"bio": "technology entrepreneur, investor, and engineer",
		"facebook": "@elonmusk",
	}
}


@app.route("/multiple/<foo>/<bar>/<baz>")
def multi(foo, bar, baz):
	return f"foo is {foo}, bar is {bar}, baz is {baz}"

@app.route("/json", methods=["POST"])
def json():
	if request.is_json:
		req = request.get_json()
		response = {
			"message": "JSON received!",
			"name": req.get("name")
		}
		res = make_response(jsonify(response), 200)
		return res
	else:
		res = make_response(jsonify({"message": "No JSON received"}), 400)
		return "No JSON receive", 400

@app.route("/guestbook")
def guestbook():
	return render_template("public/guestbook.html")

@app.route("/guestbook/create-entry", methods=["POST"])
def create_entry():
	req = request.get_json()
	print(req)
	res = make_response(jsonify(req), 200)
	return res

@app.route("/query")
def query():
	if request.args:
		args = request.args
		serialized = ", ".join(f"{k}: {v}" for k, v in args.items())
		return f"(Query) {serialized}", 200
	else:
		return "No query received", 200

app.config["IMAGE_UPLOADS"] = "/mnt/sdb1/app/app/static/img/uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

def allowed_image(filename):
	if not "." in filename:
		return False

	ext = filename.rsplit(".", 1)[1]

	if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
		return True
	else:
		return False


def allowed_image_filesize(filesize):
	if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
		return True
	else:
		return False


@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():
	if request.method == "POST":
		if request.files:

			if not allowed_image_filesize(request.cookies.get("filesize")):
				print("File exxeeded maximum size")
				return redirect(request.url)
			
			image = request.files["image"]
			
			if image.filename == "":
				print("Image must have a filename")
				return redirect(request.url)

			if not allowed_image(image.filename):
				print("That image extension is not allowed")
				return redirect(request.url)

			else:
				filename = secure_filename(image.filename)

			image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
			print("Image saved")
			return redirect(request.url)

	return render_template("public/upload_image.html")

@app.route("/cookies")
def cookies():
	res = make_response("Cookies", 200)
	cookies = request.cookies
	flavor = cookies.get("flavor")
	choc_type = cookies.get("chocolate type")
	chewy = cookies.get("chewy")
	print(flavor, choc_type, chewy)
	res.set_cookie(
		"flavor", 
		value="chocolate chip",
		max_age=10,
		expires=None,
		path=request.path,
		domain=None,
		secure=False,
		httponly=False
		)
	res.set_cookie("Chocolate type", "dark")
	res.set_cookie("chewy", "yes")
	return res

from flask import render_template, request, session, redirect, url_for

app.config["SECRET_KEY"] = "Eyc2sa8c_HJBU-qnYi4BRA"

users = {
    "julian": {
        "username": "julian",
        "email": "julian@gmail.com",
        "password": "example",
        "bio": "Some guy from the internet"
    },
    "clarissa": {
        "username": "clarissa",
        "email": "clarissa@icloud.com",
        "password": "sweetpotato22",
        "bio": "Sweet potato is life"
    }
}


@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
	if request.method == "POST":
		req = request.form
		username= req.get("username")
		password = req.get("password")

		if not username in users:
			print("username not found")
			return redirect(request.url)
		else:
			user = users[username]

		if not password == user["password"]:
			print("Password_incorect")
			return redirect(request.url)
		else:
			session["USERNAME"] = user["username"]
			session["PASSWORD"] = user["password"]
			print("User added to session")
			return redirect(url_for("profile"))

	return render_template("public/sign_in.html")

@app.route("/profile")
def profile():
	if not session.get('USERNAME', None) is not None:
		username = session.get("USERNAME")
		user = users[username]
		return render_template("public/profile.html", user=user)
	else:
		print("USername not found in session")
		return redirect(url_for("sign-in"))