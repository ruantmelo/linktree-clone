from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate
from utils import login_required
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

social_networks = db.Table('users_social_networks',
                            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                            db.Column('social_network_id', db.Integer, db.ForeignKey('social_network.id'))
                            )

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    summary = db.Column(db.String(200), nullable=True)
    social_networks = db.relationship('SocialNetwork', secondary=social_networks, lazy='subquery')

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('links', lazy=True))
    label = db.Column(db.String(40), nullable=False)
    
class SocialNetwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    prefix = db.Column(db.String(40), nullable=True)


@app.after_request
def after_request(r):
    """Ensure responses aren't cached"""
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    user = User.query.get(user_id)

    return render_template("index.html", name=user.name, summary=user.summary, links=user.links)

@app.route("/login", methods=['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')

        if not email:
            return render_template("login.html", error="Password is required.")

        if not password:
            return render_template("login.html", error="Password is required.")

        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template("login.html", error="Email or password is incorrect.")
        
        password_match = bcrypt.check_password_hash(user.password, password)

        if not password_match:
            return render_template("login.html", error="Email or password is incorrect.")
        
        session['user_id'] = user.id

        return redirect("/")

        
    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmation = request.form.get("confirmation")

        if not name:
            return render_template("register.html", error="Name is required.")

        if not email:
            return render_template("register.html", error="Email is required.")

        if not password:
            return render_template("register.html", error="Password is required.")
        
        if password != confirmation:
            return render_template("register.html", error="Passwords do not match.")

        user = User.query.filter_by(email=email).first()

        if user:
            return render_template("register.html", error="Email is already in use.")

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(name=name, email=email, password=password_hash)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

        return redirect("/")
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")