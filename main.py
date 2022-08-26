 
#import email
import os
from flask import Flask, render_template, redirect, url_for ,flash,abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from forms import CreatePostForm, LoginForm , RegisterForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_ckeditor import CKEditor, CKEditorField
import data_request
from functools import wraps

app = Flask(__name__)
#app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
#app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager=LoginManager()
login_manager.init_app(app)
##CONNECT TO DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testdata2907.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

#ENV = 'prod'
ENV = 'dev'

if ENV =='dev':
  app.debug=True
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/Mydb'
else:
  app.debug=False
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yphlpmwxtrjpse:a8938f30223b728bbacc29e648f267c950ae5112cc533891e5563f29daae29b7@ec2-52-71-23-11.compute-1.amazonaws.com:5432/delpgdkrofc906'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

user_word = db.Table('user_word',
  db.Column('user_id',db.Integer,db.ForeignKey('user.id')),
  db.Column('word_id',db.Integer,db.ForeignKey('word.id'))
)

class User(UserMixin,db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(100), unique=True)
  password= db.Column(db.String(100))
  name= db.Column(db.String(100))
  password2= db.Column(db.String(100))
  ##
  words = db.relationship('Word',secondary=user_word , backref='words')

class Word(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  author = relationship("User", back_populates="words")
  title = db.Column(db.String(250), unique=True, nullable=False)
  part_speech= db.Column(db.String(250), nullable=True)
  definition= db.Column(db.String(250), nullable=True)
  example_sentence= db.Column(db.String(250), nullable=True)
  audio_file= db.Column(db.String(250), nullable=True)
  date = db.Column(db.String(250), nullable=False)

def admin_only(f):
  @wraps(f)
  def decorated_function(*args,**kwargs):
    if current_user.id != 1:
      return abort(403)
    return f(*args,**kwargs)
  return decorated_function

# Load User
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

# Home
@app.route('/index')
@login_required
def home():
  words = Word.query.all()
  try:
    user_words= current_user.words
    min_index=user_words[0].id
  except:
    min_index=0
  return render_template("home/index.html",all_words=words,num_words=len(words),num_user_words=len(user_words),user_words=user_words,min_index=min_index, current_user=current_user)

# Request New Word
@app.route('/request-new-word' ,methods=["GET", "POST"])
def request_new_word():
  form = CreatePostForm()
  if form.validate_on_submit():
    word_exsist=db.session.query(Word).filter_by(title=form.title.data).first()
    if word_exsist:
      print("Word exsist in data")
    else:
      request_word=data_request.translate_word(form.title.data)
      new_word = Word(
        title=form.title.data.title(),
        part_speech=request_word["part-speech"],
        definition=request_word["Definition"][0],
        example_sentence=request_word["Example sentence"][0]["text"],
        audio_file=request_word["audio-file"],
        author_id=current_user.id,
        date=date.today().strftime("%B %d, %Y"),
      )
      db.session.add(new_word)
      current_user.words.append(new_word)
      db.session.commit()
    return redirect(url_for("home"))
  return render_template("home/make_word.html",min_index=0, form=form ,current_user=current_user)

# Add New Word
@app.route('/new-word' ,methods=["GET", "POST"])
def add_new_word():
  form = CreatePostForm()
  if form.validate_on_submit():
    word_exsist=db.session.query(Word).filter_by(title=form.title.data).first()
    if word_exsist:
      current_user.words.append(word_exsist)
      db.session.commit()
    else:
      request_new_word()
    return redirect(url_for("home"))
  return render_template("home/make_word.html",min_index=0, form=form ,current_user=current_user)
 
#Show Card
@app.route('/card/<int:word_id>')
def show_card(word_id):
  word_list= current_user.words
  if(len(word_list)==0):
    print("No data on this User")
    return redirect(url_for("home"))
  print(word_list)
  next_word_id=next_word(word_id,word_list).id 
  requested_word=db.session.query(Word).filter_by(id=word_id).first()
  return render_template("home/card.html",word=requested_word,current_user=current_user,next_word=next_word_id,min_index=word_id)

def next_word(word_id,word_list):
  newlist = [x.id for x in word_list]
  word_index=newlist.index(word_id)
  try:
    next_word=word_list[word_index+1]
  except:
    next_word=word_list[0]
  return next_word

# Delete word from DB
@app.route("/delete/<int:word_id>")
@admin_only
def delete_card(word_id):
    word_to_delete = Word.query.get(word_id)
    db.session.delete(word_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

# Remove word from User
@app.route("/remove/<int:word_id>")
def remove_card(word_id):
    word_to_delete = Word.query.get(word_id)
    current_user.words.remove(word_to_delete)
     
    db.session.commit()
    return redirect(url_for('get_all_posts'))

#logout_user
@app.route("/logout")
def logout():
  logout_user()
  return redirect(url_for('login'))

#about
@app.route("/about")
def about():
  return render_template("about.html",current_user=current_user)

#contact
@app.route("/contact")
def contact():
  return render_template("contact.html",current_user=current_user)

# Add New User
@app.route('/register',methods=["GET","POST"])
def register():
  form = RegisterForm()
  if form.validate_on_submit():

    if User.query.filter_by(email=form.email.data).first():
      flash("You've already signed up with that email,log in instead!")
      return redirect(url_for('login'))

    hash_and_salted_password = generate_password_hash(
      form.password.data,
      method='pbkdf2:sha256',
      salt_length=8
    )

    new_user=User(
      email=form.email.data,
      name=form.name.data,
      password=hash_and_salted_password,
      password2=form.password.data
    )

    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return redirect(url_for("home"))
  return render_template("login/register.html",form=form , current_user=current_user)

# Login User
@app.route('/',methods=["GET","POST"])
def login():
  form = LoginForm()

  if form.validate_on_submit():
    email=form.email.data
    password=form.password.data
    user=User.query.filter_by(email=email).first()

    if not user:
      flash("That email does not exist, please try again.")
      return redirect(url_for('login'))
    elif not check_password_hash(user.password,password):
      flash("Password incorrect, please try again.")
      return redirect(url_for('login'))  

    else:
      login_user(user)
      return redirect(url_for('home'))
  return render_template("login/login.html",form=form , current_user=current_user)  

if __name__ == "__main__":
  app.run()

