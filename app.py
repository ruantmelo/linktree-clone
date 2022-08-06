from crypt import methods
from unicodedata import category
from flask import Flask,abort, render_template, request, redirect, session, jsonify
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
                        
class UsersSocialNetworks(db.Model):
    __tablename__ = 'users_social_networks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    social_network_id = db.Column(db.Integer, db.ForeignKey('social_network.id'), nullable=False)
    url = db.Column(db.String(120), nullable=False)
    user = db.relationship('User', back_populates='social_networks')
    social_network = db.relationship('SocialNetwork', back_populates='users')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    summary = db.Column(db.String(200), nullable=True)
    social_networks = db.relationship('UsersSocialNetworks', back_populates="user", lazy='subquery')

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
    users = db.relationship('UsersSocialNetworks', back_populates="social_network", lazy='subquery')


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
    user_social_networks = user.social_networks

    return render_template("index.html", name=user.name, summary=user.summary, links=user.links, user_social_networks = user_social_networks, is_owner = True)

@app.route("/login", methods=['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')

        if not email or email.strip() == '':
            return render_template("login.html", error="Email is required."), 400

        email = email.lower().strip()

        if not password:
            return render_template("login.html", error="Password is required."), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template("login.html", error="Email or password is incorrect."), 400
        
        password_match = bcrypt.check_password_hash(user.password, password)

        if not password_match:
            return render_template("login.html", error="Email or password is incorrect."), 400
        
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
        
        if not name or name.strip() == '':
            return render_template("register.html", error="Name is required."), 400

        if not email or email.strip() == '':
            return render_template("register.html", error="Email is required."), 400

        email = email.lower().strip()

        if not password:
            return render_template("register.html", error="Password is required."), 400
        
        if password != confirmation:
            return render_template("register.html", error="Passwords do not match."), 400

        user = User.query.filter_by(email=email).first()

        if user:
            return render_template("register.html", error="Email is already in use."), 400

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

@app.route("/edit", methods=['GET', 'POST'])
@login_required
def edit():
    user_id = session["user_id"]
    user = User.query.get(user_id)
    social_networks = SocialNetwork.query.all()
    user_social_networks = user.social_networks

    if request.method == "POST":
        if not user:
            return jsonify({"error": "Session error"}), 400

        data = request.get_json()
        new_summary = data.get("summary")
        new_link = data.get("link")
        new_social_network = data.get("social_network")

        if new_summary != None:
            user.summary = new_summary
        
        if new_link != None:
            label = new_link.get("label")
            url = new_link.get("url")
            if label == None:
                return jsonify({"error": "Label is required."}), 400
            
            if url == None:
                return jsonify({"error": "URL is required."}), 400

            link = Link(url=url, user=user, label=label)
            db.session.add(link)
        
        if new_social_network != None:
            social_network_id = int(new_social_network.get("id"))
            url = new_social_network.get("url")

            if not social_network_id:
                return jsonify({"error": "Social network is required."}), 400
            
            if not url:
                return jsonify({"error": "URL is required."}), 400
            
            find_social_network = SocialNetwork.query.get(social_network_id)

            if not find_social_network:
                return jsonify({"error": "Social network is not valid."}), 400
            
            find_user_social_network = UsersSocialNetworks.query.filter_by(user_id=user_id, social_network_id=social_network_id).first()

            if find_user_social_network:
                return jsonify(message=f"User already has this social network ({find_social_network.name}).", type="error"), 400
            
            user_social_network = UsersSocialNetworks(user=user, social_network=find_social_network, url=url)
            db.session.add(user_social_network)
        
        db.session.commit()

        return "success"
        
    
    user_social_networks_ids = []
    for user_social_network in user_social_networks:
        user_social_networks_ids.append(user_social_network.social_network_id)
    
    social_networks_available = []

    for social_network in social_networks:
        if social_network.id not in user_social_networks_ids:
            social_networks_available.append(social_network)

    return render_template("edit.html", summary=user.summary, links=user.links, social_networks_available=social_networks_available, user_social_networks=user_social_networks)


@app.route("/links/<int:link_id>", methods=['DELETE'])
@login_required
def delete_link(link_id):
    if not link_id:
        return jsonify({"error": "Link id is required."}), 400

    link = Link.query.get(link_id)

    if not link:
        return jsonify({"error": "Link is not valid."}), 400

    user_id = session["user_id"]
    
    if link.user_id != user_id:
        return jsonify({"error": "Link is not valid."}), 400

    db.session.delete(link)
    db.session.commit()

    return "success" 

@app.route("/users-social-networks/<int:user_social_network_id>", methods=['DELETE'])
@login_required
def delete_user_social_networks(user_social_network_id):
    if not user_social_network_id:
        return jsonify({"error": "User Social Network ID is required."}), 400

    user_social_network = UsersSocialNetworks.query.get(user_social_network_id)

    if not user_social_network:
        return jsonify({"error": "User Social Network ID is not valid."}), 400
    
    user_id = session["user_id"]

    if user_social_network.user_id != user_id:
        return jsonify({"error": "User Social Network ID is not valid."}), 400

    db.session.delete(user_social_network)
    db.session.commit()

    return "success"

@app.route("/<int:user_id>")
def view(user_id):
    if not user_id:
        return jsonify({"error": "User id is required."}), 400
    
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User is not valid."}), 400
    user_social_networks = user.social_networks

    is_owner = user_id ==  session.get("user_id")

    return render_template("index.html", name=user.name, summary=user.summary, links=user.links, user_social_networks=user_social_networks, is_owner=is_owner)
