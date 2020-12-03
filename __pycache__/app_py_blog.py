from datetime import datetime
import flask_login
import yaml
import pdb
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from config import mail_username, mail_password



app = Flask(__name__)


app.config['TESTING'] = False
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Desktop/Lesenswert/blog2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
app.config['MAIL_DEBUG'] = True

db = SQLAlchemy(app)
mail = Mail(app)


login_manager = LoginManager()
login_manager.init_app(app)


with open(r'C://Users//Desktop//Yaml//application.yaml') as file:
    users = yaml.full_load(file)


class User(UserMixin):
    pass



class Blogpost2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)


db.create_all()  



@app.route('/contact', methods=["POST", "GET"])
def contact():

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        phone = request.form.get('phone')        
        msg = Message(subject=f"E-Mail da {name}", body=f"Name: {name}\nE-Mail: {email}\nTelefono: {phone}\nMessaggio: {message}", sender="francesco.leonelli84@gmail.com", recipients=['francesco.leonelli84@gmail.com'])
            
        mail.send(msg)
            
        return render_template('contact.html', success=True) 

    return render_template('contact.html') 



@app.route('/')
def index():
    posts = Blogpost2.query.order_by(Blogpost2.date_posted.desc()).all()

    return render_template('index.html', posts=posts)



@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/post/<int:post_id>', methods=['POST','GET'])
def post(post_id):
    post = Blogpost2.query.filter_by(id=post_id).one()  

    date_posted = post.date_posted.strftime('%d %B, %Y')

    return render_template('post.html', post=post, date_posted=date_posted)




@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return

    user = User()
    user.id = username
    return user



@login_manager.request_loader
def request_loader(request):
    username = request.form.get("username")  
    if username not in users:
        return
    user = User()
    user.id = username
    user.is_authenticated = request.form["pw"] == users[username]["pw"]

    return user


@app.route('/login', methods=["POST", "GET"])
def login():
    error = None
    try: 
     if request.method == 'POST':
        username = request.form.get('username')
        if request.form.get('pw') == users[username]["pw"]:
            user = User()
            user.id = username
            flask_login.login_user(user)
            return redirect(url_for("add"))
    except (KeyError, AttributeError):
        error = "Leider haben Sie die falschen Zugangsdaten."
        return render_template("login.html", error=error)
    return render_template("login.html")


@app.route('/add')
@login_required
def add():
    return render_template('add.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/prova')
def prova():
    return render_template('prova.html')


@app.route('/addpost', methods=['POST'])
def addpost():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form["author"]
    content = request.form['content']

    post = Blogpost2(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now())

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(debug=True)


