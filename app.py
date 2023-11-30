import sqlite3
from flask import Flask,session,render_template,request,g,redirect,url_for
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail, Message
import smtplib

app=Flask(__name__)
app.secret_key= "randomly_42"
app.config["SESSION_COOKIE_NAME"] = "cookie_42_haha"

@app.before_request
def require_login():
    if request.endpoint not in ['login', 'signup', 'index','loginadmin'] and 'user' not in session:
        return redirect('/')


@app.route("/",methods=["POST","GET"])
def index():
    return render_template("index.html")

@app.route("/welcome/<user>", methods=["GET","POST"])
def welcome(user):
    if 'user' in session and session['user'] == user:
        data = get_db()
        return render_template("welcome.html", all_data=data, user=user)
    else:
        return redirect('/')


@app.route('/paid/<user>/<seats>/<id>/<m>', methods=['POST'])
def paid(user,seats,m,id):
    mail=get_user(user)[1]
    msg=f"Hello {user}! You just bought {seats} seats for show - {m} \n Booking id - {id}"
    message = f'''Subject: Booking Confirmation
            
    
            {msg}'''
    sender_email = 'project.for.iitm@gmail.com'
    recipient_email = mail
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, 'dilqxbeleptdpfpg')
            server.sendmail(sender_email, [recipient_email], message)
            return redirect(url_for('welcome', user=user))
    except Exception as e:
        return f"Error sending email: {str(e)}"

@app.route("/buyseats/<user>/<id>", methods=["GET","POST"])
def buyseats(user,id):
    seat_name = f"seat{id}"
    seats = request.form[seat_name]
    d=get_show(id)
    m=d[1]
    s=d[2]
    if int(s)>=int(seats):
        sleft=int(s)-int(seats)
        db=sqlite3.connect('db.db')
        cursor=db.cursor()
        query="""UPDATE shows SET seats=? WHERE id = ?"""
        cursor.execute(query,(sleft,id))
        db.commit()
        db.close()
        book(id,user,seats)
        return render_template("buyseats.html",user=user,m=m,seats=seats,id=id)
    return render_template("buyseats.html",error=f"Asking for {seats} seats. \nOnly {s} left. ")

@app.route('/signup', methods=["GET", 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('mail')
        phone = request.form.get('phone')

        if username and password and (email or phone):
            try:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())                
                db = sqlite3.connect('db.db')
                cursor = db.cursor()
                cursor.execute("INSERT INTO users (username, hashp, mail, phone) VALUES (?, ?, ?, ?)",
                               (username, hashed_password, email, phone))
                db.commit()
                db.close()
                session['user'] = username
                return redirect(url_for("welcome", user=username))
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed: users.username" in str(e):
                    error = "Username already exists. Please choose a different username."
                elif "UNIQUE constraint failed: users.phone" in str(e):
                    error = "Phone number already exists."
                elif "UNIQUE constraint failed: users.mail" in str(e):
                    error = "Email already exists."                
                else:
                    error = str(e)
        else:
            error = "Please provide a username, password, and either email or phone number."
    elif request.method == 'GET':
        return render_template("signup.html")
    return render_template("signup.html",error=error)

@app.route('/login', methods=["GET",'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            user = get_user(username)
            if user and bcrypt.checkpw(password.encode('utf-8'), user[4]):
                session['user'] = user[3]
                return redirect(url_for('welcome', user=username))
            else:
                error = "Invalid credentials. Please try again."
        else:
            error = "Please provide a username and password."  
    elif request.method == 'GET':
        return render_template("login.html")  
    return render_template('login.html', error=error)

@app.route('/loginadmin', methods=["GET",'POST'])
def loginadmin():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            user = get_admin(username)
            if user and bcrypt.checkpw(password.encode('utf-8'), user[4]):
                session['user'] = user[3]
                return redirect(url_for('admin', user=username))
            else:
                error = "Invalid credentials. Please try again."
        else:
            error = "Please provide a username and password."  
    elif request.method == 'GET':
        return render_template("loginadmin.html")  
    return render_template('loginadmin.html', error=error)

@app.route("/admin/<user>", methods=["GET"])
def admin(user):
    print(session)
    data = get_db()
    return render_template("admin.html", all_data=data,user=user)


@app.route("/add_shows/<user>",methods=["POST"])
def add_shows(user):
    show = request.form["show"]
    seats = request.form["seats"]
    tprice = request.form["tprice"]
    rate = request.form["rate"]
    theatre = request.form["theatre"]
    place = request.form["place"]
    db= sqlite3.connect('db.db')
    cursor=db.cursor()
    query="""insert into shows (name,seats,tprice,ratings,theatre,place) values(?,?,?,?,?,?)"""
    cursor.execute(query,(show,seats,tprice,rate,theatre,place))
    db.commit()
    db.close()
    data = get_db() 
    return redirect(url_for("admin",user=user))

@app.route("/update_page/<user>/<id>", methods=["GET","POST"])
def update_page(user,id):
    db=sqlite3.connect('db.db')
    cursor=db.cursor()
    query="""select * FROM shows WHERE id = ?"""
    cursor.execute(query,(id,))
    show=cursor.fetchone()
    db.commit()
    db.close()
    return render_template("updatepage.html",show=show,user=user)

@app.route("/updateshow/<user>/<id>", methods=["POST"])
def updateshow(user,id):
    show=request.form["mname"]
    seats=request.form["mseats"]
    tprice=request.form["mprice"]
    rate=request.form["mrate"]
    theatre=request.form["mtheatre"]
    place=request.form["mplace"]
    db=sqlite3.connect('db.db')
    cursor=db.cursor()
    query="""UPDATE shows SET name=?,seats=?,tprice=?,ratings=?,theatre=?,place=? WHERE id = ?"""
    cursor.execute(query,(show,seats,tprice,rate,theatre,place,id))
    db.commit()
    db.close()
    return redirect(url_for("update_page",id=id,user=user))

@app.route("/delete_show/<user>/<id>", methods=["POST"])
def delete_show(user,id):
    db=sqlite3.connect('db.db')
    cursor=db.cursor()
    query="""DELETE FROM shows WHERE id = ?"""
    cursor.execute(query,(id,))
    db.commit()
    db.close()
    return redirect(url_for("admin",user=user))
    
@app.route("/manadmin/<user>")
def manadmin(user):
    return render_template("manadmin.html",user=user)

@app.route("/addadmin/<user>", methods=["POST"])
def addadmin(user):
    error = None
    if request.method == 'POST':
        admin = request.form.get('newadmin')
        password = request.form.get('passadmin')
        email = request.form.get('mail')
        phone = request.form.get('phone')

        if admin and password and (email or phone):
            try:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())                
                db = sqlite3.connect('db.db')
                cursor = db.cursor()
                cursor.execute("INSERT INTO admin (username, hashp, mail, phone) VALUES (?, ?, ?, ?)",
                               (admin, hashed_password, email, phone))
                db.commit()
                db.close()
                return redirect(url_for("manadmin",user=user))
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed: admin.username" in str(e):
                    error = "Admin already exists.  "
                elif "UNIQUE constraint failed: admin.phone" in str(e):
                    error = "Phone number already exists."
                elif "UNIQUE constraint failed: admin.mail" in str(e):
                    error = "Email already exists."                
                else:
                    error = str(e)
        else:
            error = "One or more input fields not found."
    elif request.method == 'GET':
        return render_template("manadmin.html",user=user)
    return render_template("manadmin.html",error=error,user=user)

@app.route('/logout')
def logout():
    print("\n",session)
    session.pop('user', None)
    print("\n",session)
    return redirect(url_for('index'))

def get_db():
    db=sqlite3.connect('db.db')
    cursor=db.cursor()
    query="""select * from shows"""
    cursor.execute(query)
    all_data = cursor.fetchall()
    db.commit()
    db.close()
    return all_data

def get_show(id):
    db=sqlite3.connect('db.db')
    cursor=db.cursor()
    query="""select * from shows where id=?"""
    cursor.execute(query,(id,))
    all_data = cursor.fetchone()
    db.commit()
    db.close()
    return all_data

def get_user(u):
    db=sqlite3.connect('db.db')
    cursor=db.cursor()
    query="""select * from users where username=?"""
    cursor.execute(query,(u,))
    all_data = cursor.fetchone()
    db.commit()
    db.close()
    return all_data

def get_admin(u):
    db=sqlite3.connect('db.db')
    cursor=db.cursor()
    query="""select * from admin where username=?"""
    cursor.execute(query,(u,))
    all_data = cursor.fetchone()
    db.commit()
    db.close()
    return all_data

def book(sid,user,seats):
    db=sqlite3.connect('db.db')
    cursor=db.cursor()
    query="""insert into bookings (showid,user,seats) values(?,?,?)"""
    cursor.execute(query,(sid,user,seats))
    db.commit()
    db.close()
    

if __name__ == '__main__':
    app.run()