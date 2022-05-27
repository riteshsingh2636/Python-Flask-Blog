from flask import Flask, render_template, request, flash, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
from datetime import datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.bd'
app.config['SECRET_KEY'] = 'thisisserects'
db = SQLAlchemy(app)
login_manager=LoginManager() 
login_manager.init_app(app)





app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''        #Enter your email
app.config['MAIL_PASSWORD'] = ''        #Enter your email password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
s=URLSafeTimedSerializer(app.config["SECRET_KEY"])







@app.route("/reset_password")
def reset_password():
    return render_template('reset_password.html')


@app.route("/verifylink", methods=['GET', 'POST'])
def verifylink():
    if request.method=='POST':

        email = request.form['email']
        token = s.dumps(email, salt='email-confirmation-key')
        msg = Message('confirmation', sender ='ritesh123shivam@gmail.com', recipients =[email])
        link =url_for('confirm',token=token,_external=True)
        msg.body = "Your confirmation link is " + link
        user = User.query.filter_by(email=email).first()
        if user and email== user.email:
            mail.send(msg)
            flash('Reset password','success')
            return redirect('login')
        else:
            flash('Invailid Email','warning')
            return redirect('login')
    


@app.route("/confirm/<token>",methods=['GET', 'POST'])
def confirm(token):
    try:
        email= s.loads(token,salt='email-confirmation-key',max_age=600)
    except Exception:
        return "<h1> link expired </h1>"        
    user = User.query.filter_by(email=email).first()

    user.email_confirmed = True
    if request.method=='POST':
        new_password = request.form['password']
        User.query.filter_by(email=email).update(dict(password=new_password))
        db.session.commit()
        flash('Your password updated successfully','success')
        return redirect(url_for('login'))
    return render_template("create_password.html", token=token)






class User(UserMixin,db.Model):
   id = db.Column(db.Integer, primary_key = True)
   username = db.Column(db.String(120), unique=True, nullable=False)
   email = db.Column(db.String(120),  unique=True, nullable=False)
   fname = db.Column(db.String(120), nullable=False) 
   lname = db.Column(db.String(120), nullable=False)
   password = db.Column(db.String(120), nullable=False)



   def __repr__(self):
       return f"User('{self.username}','{self.email}','{self.fname}','{self.lname}','{self.password}"



class Blog(db.Model):
   blog_id = db.Column(db.Integer, primary_key = True)
   title = db.Column(db.String(80), nullable=False)
   author = db.Column(db.String(80), nullable=False)
   content = db.Column(db.Text(), nullable=False) 
   pub_date = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow) 
   def __repr__(self):
       return '<Blog %r>' % self.title



@app.route("/")
def index():
    data= Blog.query.all()
    return render_template("index.html",data=data)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route("/main")
def main():
    return render_template("main.html")


@app.route("/register", methods=['GET','POST'])
def register():
    if request.method=='POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        username = request.form.get('uname')
        email = request.form.get('email')
        password = request.form.get('password')
        # print(fname,lname,username,email,passowrd)
        user = User(fname=fname,lname=lname,username=username,email=email,password=password)
        db.session.add(user)
        db.session.commit()
        flash('user has been registerd successfully','success')
        return redirect('/login')


    return render_template("register.html")


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and password==user.password:
            login_user(user)
            return redirect('/')
        else:
            flash ('Invalid Credentials','warning')
            return redirect('/login')

    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


@app.route("/blogpost", methods=['GET','POST'])
def blogpost():
     if request.method=='POST':
        title = request.form.get('title')
        author = request.form.get('author')
        content = request.form.get('content')
        blog = Blog(title=title,author=author,content=content)
        db.session.add(blog)
        db.session.commit()
        flash("Your post has been submitted successfully",'success')
        return redirect('/')

     return render_template("blog.html")

@app.route("/blog_detail/<int:id>",methods=['GET','POST'])
def blogdetail(id):
    blog = Blog.query.get(id)
    return render_template("blog_detail.html",blog=blog)




@app.route("/delete/<int:id>",methods=['GET','POST'])
def delete_post(id):
    blog = Blog.query.get(id)
    db.session.delete(blog)
    db.session.commit()
    flash("Post has been deleted",'success')
    return redirect('/')


@app.route("/edit/<int:id>",methods=['GET','POST'])
def edit_post(id):
    blog = Blog.query.get(id)
    if request.method=='POST':
        blog.title=request.form.get('title')
        blog.author=request.form.get('author')
        blog.content=request.form.get('content')
        db.session.commit()
        flash("Post has been updated",'success')
        return redirect('/')
    return render_template("edit.html",blog=blog)



@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")




if __name__ == "__main__":
    app.run(debug=True)
























