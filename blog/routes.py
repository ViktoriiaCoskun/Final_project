from flask import Flask,render_template,request, session, flash, redirect, url_for
from . import app
from blog.models import Entry,db
from blog.forms import EntryForm,LoginForm
from faker import Faker
import functools
from flask_login import login_required,LoginManager,login_user



@app.route("/")
def index():
   generate_entries(10)
   all_posts = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())
   return render_template("homepage.html", all_posts=all_posts)

@app.route("/entry_form/<int:entry_id>", methods=["GET", "POST"])
def entry_form(entry_id):
    if session.get('logged_in'):
        if entry_id==0:
                form = EntryForm()
                errors = None
                if request.method == 'POST':
                    if form.validate_on_submit():
                        entry = Entry()
                        entry.title=form.title.data
                        entry.body=form.body.data
                        entry.is_published=form.is_published.data
                            
                        db.session.add(entry)
                        db.session.commit()
                        flash('Record was successfully created')
                        return redirect(url_for('index'))
                    else:
                        errors = form.errors
                return render_template("entry_form.html", form=form, errors=errors)
        entry = Entry.query.filter_by(id=entry_id).first_or_404()
        form = EntryForm(obj=entry)
        errors = None
        if request.method == 'POST':
            if form.validate_on_submit():
                form.populate_obj(entry)
                db.session.commit()
                flash('Record was successfully updated')
                return redirect(url_for('index'))
            else:
                errors = form.errors
        return render_template("entry_form.html", form=form, errors=errors)
    else:
       flash('Login required.', 'error')
       return redirect(url_for('login', next=request.path))
   
@app.route("/delete-post/<int:entry_id>", methods=["GET", "POST"])
#@login_required
def delete_entry(entry_id):
    if session.get('logged_in'):
        entry = Entry.query.filter_by(id=entry_id).first_or_404()
        if request.method == 'GET':
                db.session.delete(entry)
                db.session.commit()
                flash('Record was successfully deleted')
                return redirect(url_for('index'))
    else:
       flash('Login required.', 'error')
       return redirect(url_for('login', next=request.path))    
    
@app.route("/drafts/", methods=['GET'])
def list_drafts():
   if session.get('logged_in'):
       drafts = Entry.query.filter_by(is_published=False).order_by(Entry.pub_date.desc())
       return render_template("drafts.html", drafts=drafts)
   else:
       flash('Login required.', 'error')
       return redirect(url_for('login', next=request.path))

@app.route("/login/", methods=['GET', 'POST'])
def login():
   form = LoginForm()
   errors = None
   next_url = request.args.get('next')
   if request.method == 'POST':
       if form.validate_on_submit():
           session['logged_in'] = True
           session.permanent = True  # Use cookie to store session.
           flash('You are now logged in.', 'success')
           return redirect(next_url or url_for('index'))
       else:
           flash('Invalid user name or password provided', 'error')
   return render_template("login_form.html", form=form, errors=errors)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
   if request.method == 'GET':
       session.clear()
       session['logged_in'] = False
       session.permanent = True
       flash('You are now logged out.', 'success')
   return redirect(url_for('index'))

def generate_entries(how_many=10):
   fake = Faker()

   for i in range(how_many):
      post = Entry(
            title=fake.sentence(),
            body='\n'.join(fake.paragraphs(15)),
            is_published=True
      )
      db.session.add(post)
   db.session.commit()

def login_required(view_func):
   @functools.wraps(view_func)
   def check_permissions(*args, **kwargs):
       if session.get('logged_in'):
           return view_func(*args, **kwargs)
       return redirect(url_for('login', next=request.path))
   return check_permissions