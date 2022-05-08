
from flask import Flask,render_template,redirect,url_for,request,flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import UserMixin,login_required
from passlib.hash import sha256_crypt
from functools import wraps
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Enter-Your-todo.db-path-here\Flask-Todo-App/todo.db'
app.secret_key = '*/--chofhAC5__5/85/JE6fDE3f589655/*445deFEdfdgcx__**/45ddsgg'

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You can't reach this page without login","danger")
            return redirect(url_for("login"))

    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/todos")
@login_required
def todos():
    username=session["name"]
    user=User.query.filter_by(name=username).first()
    user_id=user.id
    todos = Todo.query.filter_by(user_id=user_id)
    todos=list(todos)
    return render_template("todos.html",todos = todos)


@app.route("/account/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":  
        name=request.form.get("name")
        password=request.form.get("password")
        email_check = User.query.filter_by(name=name).first()
        if email_check:
            if sha256_crypt.verify(password,email_check.password):
                flash("You Have Login Successfully","success")
                session["logged_in"] = True
                session["name"] = name
                return redirect(url_for("index"))
            else:
                flash("Wrong Password","danger")
                return redirect(url_for("login")) 
        else:
            flash("There is no such user","danger") 
            return redirect(url_for("login"))       

    return render_template("login.html")


@app.route("/account/register",methods = ["GET","POST"])
def register():
    
    if request.method == "POST":
        password=request.form.get("password")
        email=request.form.get("email")
        name=request.form.get("name")

        email_check = User.query.filter_by(email=email).first()
        if email_check:
            flash("This email is already taken","danger")  
            return redirect(url_for("register"))
        elif len(name) > 20:
            flash("Name length can't bigger than 20 charachter","danger")  
            return redirect(url_for("register"))  
        elif len(password) < 8:
            flash("Password length can't smaller than 8 charachter","danger")  
            return redirect(url_for("register"))         
        else:
            password=sha256_crypt.encrypt(request.form.get("password"))
            user = User(password=password,name=name,email=email)
            db.session.add(user)
            db.session.commit() 
            flash("You have registered successfully","success") 
            return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/account/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))



@app.route("/complete/<string:id>")
@login_required
def completeTodo(id):
    username=session["name"]
    user=User.query.filter_by(name=username).first()
    user_id=user.id
    todo = Todo.query.filter_by(id = id,user_id=user_id).first()
    if todo:
        todo.complete = not todo.complete
        db.session.commit()
        flash("You have updated successfully","success") 
        return redirect(url_for("todos"))
    else:
        flash("Something Wrong","danger") 
        return redirect(url_for("todos"))

@app.route("/add",methods = ["POST"])
@login_required
def addTodo():

    username=session["name"]
    user=User.query.filter_by(name=username).first()
    user_id=user.id
    title = request.form.get("title")
    newTodo = Todo(title = title,complete = False,user_id=user_id)
    db.session.add(newTodo)
    db.session.commit()

    return redirect(url_for("todos"))


@app.route("/delete/<string:id>")
@login_required
def deleteTodo(id):
    username=session["name"]
    user=User.query.filter_by(name=username).first()
    user_id=user.id
    todo = Todo.query.filter_by(id = id,user_id=user_id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        flash("You have deleted successfully","success") 
        return redirect(url_for("todos"))
    else:
        flash("Something Wrong","danger") 
        return redirect(url_for("todos"))


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    title = db.Column(db.String(80))
    complete = db.Column(db.Boolean,default=False)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(20))
    todos = db.relationship('Todo', backref='owner', lazy=True)



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
    csrf.init_app(app)