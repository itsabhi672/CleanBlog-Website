import datetime
import os
import json
from flask import Flask, render_template, redirect, request, url_for, session
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

with open("config.json", "r") as file:
    params = json.load(file)["params"]

number = params["no_of_blogs"]

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contact_form_data.db"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('URI_KEY')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy()
db.init_app(app)

mail = Mail(app)
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT="25",
    MAIL_USE_TLS=True,
    MAIL_USERNAME= os.environ.get('EMAIL'),
    MAIL_PASSWORD= os.environ.get('PASSWORD'),
)
mail.init_app(app)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)

class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String, nullable=False)
    s_no = db.Column(db.String, unique=True, nullable=False)

with app.app_context():
    db.create_all()


@app.route("/")
def home_page():
    posts = db.session.execute(db.select(Blogs)).scalars().all()[0:number]
    today = datetime.datetime.now().day
    return render_template('home.html', blogs=posts, day=today)


@app.route("/about")
def about_page():
    return render_template('about.html')


@app.route("/contact", methods=['GET', 'POST'])
def contact_page():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone_num']
        message = request.form['msg']
        entry = Contact(name=name, email=email, phone=phone, message=message)
        db.session.add(entry)
        db.session.commit()
        mail.send_message(
            f"New message from {name}",
            sender=f"{email}",
            recipients=[os.environ.get('EMAIL')],
            body=f"{message} \nPhone no. {phone}"
        )
        return redirect(url_for('contact_page'))
    return render_template('contact.html')


@app.route("/post/<int:id>")
def post_page(id):
    blog = db.session.execute(db.select(Blogs)).scalars().all()[0:number]
    return render_template("post.html", blog=blog, id=id)


@app.route("/dashboard", methods=['GET', 'POST'])
def dash_board():
    if 'user' in session and session['user'] == params['admin_username']:
        posts = db.session.execute(db.select(Blogs)).scalars().all()
        return render_template('dashboard.html', posts=posts)

    if request.method == 'POST':
        username = request.form.get("admin_name")
        password = request.form.get("admin_pass")
        if username == params['admin_username'] and password == params['admin_password']:
            session['user'] = username
            posts = db.session.execute(db.select(Blogs)).scalars().all()
            return render_template("dashboard.html", posts=posts)
    else:
        return render_template('login.html')

# @app.route("/edit/<string:sno>", methods=['GET', 'POST'])
# def edit_post(sno):
#     if 'user' in session and session['user'] == params['admin_username']:
#         if request.method == 'POST':
#             pass



if __name__ == "__main__":
    app.run(debug=True)
