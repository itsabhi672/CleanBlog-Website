import datetime
from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import requests

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contact_form_data.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:karan_gupta00@db.rxsvgyongqaipfbbykwk.supabase.co:5432/postgres"
db = SQLAlchemy()
db.init_app(app)

mail = Mail(app)
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT="25",
    MAIL_USE_TLS=True,
    MAIL_USERNAME="itsabhi769@gmail.com",
    MAIL_PASSWORD="glaehvpmefxkzobs",
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

with app.app_context():
    db.create_all()

# posts = requests.get(url='https://api.npoint.io/e2c47c9f03d84125c671').json()

@app.route("/")
def home_page():
    posts = db.session.execute(db.select(Blogs)).scalars().all()
    today = datetime.datetime.now().day
    return render_template('home.html', blogs=posts, day=today, post=posts)


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
            recipients=["itsabhi769@gmail.com"],
            body=f"{message} \nPhone no. {phone}"
        )
        return redirect(url_for('contact_page'))
    return render_template('contact.html')


# @app.route("/post/<int:index>")
# def post_page(index):
#     posts = db.session.execute(db.select(Blogs)).scalars().all()
#     requested_post = None
#     for blog_post in posts:
#         if blog_post["id"] == index:
#             requested_post = blog_post
#
#     return render_template("post.html", post=requested_post)


@app.route("/dashboard")
def dash_board():
    return render_template('login.html')



if __name__ == "__main__":
    app.run(debug=True)
