from flask import Flask,redirect,render_template,request,url_for,session,flash,send_file
from flask_session import Session
from flask_mysqldb import MySQL
from io import BytesIO# the files are in the form of bytes
import io
from otp import genotp
from cmail import sendmail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
import random
app=Flask(__name__)
app.secret_key='23efgbnjuytr'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='spm'
Session(app)
mysql=MySQL(app)
@app.route('/')
def index():#register or login page route
    return render_template('index.html')
@app.route('/registration', methods=['GET','POST'])
def register():#register route
    if request.method=='POST':
        rollno=request.form['rollno']
        name=request.form['name']
        group=request.form['group']
        password=request.form['password']
        email=request.form['email']
        code=request.form['code']
#define college code
        ccode='sdmsmkpbsc$#23'
        if ccode==code:
            #we are handling the code in the 2 forms 1.try and catch 2.connect to database and access the values
            #if the value is already is exit then we handle and show some message
            #retriving all the values of rollno,email check wether they are unique or not
            cursor=mysql.connection.cursor()
            cursor.execute('select rollno from students')
            data=cursor.fetchall()
            cursor.execute('select email from students')
            edata=cursor.fetchall()
            #print(data)
            if (rollno,)in data:# the data is return in the form of tuple then we use (rollno,)
                #and all the rollno data is present in tha data it check the condition
                #if the given number is already present in the database then it diaplay the message
#user already exits
                #and display the same register.html page
                flash('user already exits')
                return render_template('register.html')
            if (email,)in edata:
                flash('email already exits')
                return render_template('register.html')
                cursor.close()
                otp=genotp()
                subject='thanks for registering'
                body=f'use this otp register {otp}'
                sendmail(email,subject,body)
                return render_template('otp.html',otp=otp,rollno=rollno,name=name,group=group,password=password,email=email)

            else:
                flash('invalid college code')
                return render_template('register.html')
        
    return render_template('register.html')
@app.route('/login',methods=['GET','POST'])#after register login with rollno and password route
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        rollno=request.form['id']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from students where rollno=%s and password=%s',[rollno,password])#if the count is 0 then either username or password is wrong or if it is 1 then it is login successfully
        count=cursor.fetchall()[0]
        if count==0:
            flash('Invalid username or password')
            return render_template('logic.html')
        else:
            session['user']=rollno
            return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/studenthome')#notes,files,back (home page)route
def home():
    if session.get('user'):
        return render_template('home.html')
    else:
        flash("login first")#implemente flash
        return redirect(url_for('login'))
@app.route('/logout')#logout route
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('index'))
    else:
        flash('u are already logged out!')
        return redirect(url_for('login'))
@app.route('/otp/<otp>/<rollno>/<name>/<group>/<password>/<email>',methods=['GET','POST'])
def otp(otp,rollno,name,group,password,email):#validate the sended otp with given otp 
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:#checking for entered otp is similar as sended otp
#after that inserting the values of the users in the database
            cursor=mysql.connection.cursor()
            cursor.execute('insert into students values(%s,%s,%s,%s,%s)',(rollno,name,group,password,email))
            mysql.connection.commit()
            cursor.close()
            flash('Details Registered')#send mail to the user as successful registration
            return redirect(url_for('login'))
        else:
            flash('wrong otp')
            return render_template('otp.html',otp=otp,rollno=rollno,name=name,group=group,password=password,email=email)
@app.route('/noteshome')
def notehome():#notes route
    if session.get('user'):
        rollno=session.get('user')
        cursor=mysql.connection.cursor()
        cursor.execute('select * from notes where rollno=%s',[rollno])
        notes_data=cursor.fetchall()
        print(notes_data)
        cursor.close()
        return render_template('addnotetable.html',data=notes_data)
    else:
        return redirect(url_for('login'))
@app.route('/addnotes',methods=['GET','POST'])
def addnote():
    if session.get('user'):
        if request.method=='POST':
            title=request.form['title']
            content=request.form['content']
            cursor=mysql.connection.cursor()
            rollno=session.get('user')
            cursor.execute('insert into notes(rollno,title,content) values (%s,%s,%s)',[rollno,title,content])
            mysql.connection.commit()
            cursor.close()
            flash(f'{title} added successfully')
            return redirect (url_for('notehome'))
            
            
        return render_template('notes.html')
    else:
        return redirect(url_for('login'))
@app.route('/viewnotes/<nid>')
def viewnotes(nid):#view(or read notes)route
    cursor=mysql.connection.cursor()
    cursor.execute('select title,content from notes where nid=%s',[nid])
    data=cursor.fetchone()#to fetch single row
    return render_template('notesview.html',data=data)
@app.route('/updatenotes/<nid>',methods=['GET','POST'])
def updatenotes(nid):#update(or write)notes route
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select title,content from notes where nid=%s',[nid])
        data=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
            title=request.form['title']
            content=request.form['content']
            cursor=mysql.connection.cursor()
            cursor.execute('update notes set title=%s,content=%s where nid=%s',[title,content,nid])
            mysql.connection.commit()
            cursor.close()
            flash('notes updated successfully')
            return redirect(url_for('notehome'))
        return render_template('notesupdate.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/deteletnotes/<nid>')
def deletenotes(nid):#to delete the record or notes
    cursor=mysql.connection.cursor()
    cursor.execute('delete from notes where nid=%s',[nid])
    mysql.connection.commit()
    cursor.close()
    flash('notes deleted successfully')
    return redirect(url_for('notehome'))
@app.route('/fileshome')#files routes
def fileshome():
    if session.get('user'):
        rollno=session.get('user')
        cursor=mysql.connection.cursor()
        cursor.execute('select fid,filename,data from files where rollno=%s',[rollno])
        data=cursor.fetchall()# the query is returing multiple values
        cursor.close()
        return render_template('fileuploadtable.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/filehandling',methods=['POST'])
def filehandling():
    file=request.files['file']# to handle the file data
    #no need to check wether the user is present in the database or becoz
    #1.we are using the post when the user click on the submit then no need to check the user
#is present or not
    #2.if we are accessing the this url in the search box it not found
    filename=file.filename#name of the file
    bin_file=file.read()#to read the file 
    rollno=session.get('user')
    cursor=mysql.connection.cursor()
    cursor.execute('insert into files(rollno,filename,filedata)values(%s,%s,%s)',[rollno,filename,bin_file])
    mysql.connection.commit()
    cursor.close()
    flash(f'{filename}uploaded successfully')
    return redirect(url_for('fileshome'))
@app.route('/viewfile/<fid>')
def viewfile(fid):#to view the uploded file
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select filename,filedata from files where fid=%s',[fid])
        data=cursor.fetchone()
        cursor.close()
        filename=data[0]
        bin_file=data[1]#unicode data(binary string-data)
        byte_data=BytesIO(bin_file)#covert binary file to bytes
        return send_file(byte_data,download_name=filename)#arguments of send_file(1st is byte data file
    #2.to convert the file in the given extension like(txt,pic,pdf)we need filename
    #if we want only the pdf file we use the mime_type(explicit convertion))
    else:
        return redirect(url_for('login'))
@app.route('/filedownload/<fid>')
def filedownload(fid):#to dwonload  the file
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select filename,filedata from files where fid=%s',[fid])
        data=cursor.fetchone()
        cursor.close()
        filename=data[0]
        bin_file=data[1]#unicode data(binary string-data)
        byte_data=BytesIO(bin_file)#covert binary file to bytes
        return send_file(byte_data,download_name=filename,as_attachment=True)#arguments of send_file(1st is byte data file
    #2.to convert the file in the given extension like(txt,pic,pdf)we need filename
    #3.to download a file we use the as_attachment=True
    #if we want only the pdf file we use the mime_type(explicit convertion))
    else:
        return redirect(url_for('login'))        
@app.route('/filedelete/<fid>')
def filedelete(fid):# to delete the file
    cursor=mysql.connection.cursor()
    cursor.execute('delete from files where fid=%s',[fid])
    mysql.connection.commit()
    flash('File deleted successfully')
    return redirect (url_for('fileshome'))
    
@app.route('/forgetpassword',methods=['GET','POST'])
def forget():#after clicking the forget password
    if request.method=='POST':
        rollno=request.form['id']# store the id in the rollno
        cursor=mysql.connection.cursor()#connection to mysql
        cursor.execute('select rollno from students')# fetch the rollno data in the table students
        data=cursor.fetchall()#fetching all the rollno data and store it in the "data" variable 
        if (rollno,) in data:# if the given rollno of the user is present in tha database->data
            cursor.execute('select email from students where rollno=%s',[rollno])#it fetches email related to the rollno 
            data=cursor.fetchone()[0]#fetch the only one email related to the rollno 
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the password using-{request.host+url_for("createpassword",token=token(rollno,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid user id'
    return render_template('forgot.html')
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):#to create noe password and conform the password
        try:
            s=Serializer(app.config['SECRET_KEY'])
            rollno=s.loads(token)['user']
            if request.method=='POST':
                npass=request.form['npassword']
                cpass=request.form['cpassword']
                if npass==cpass:
                    cursor=mysql.connection.cursor()
                    cursor.execute('update students set password=%s where rollno=%s',[npass,rollno])
                    mysql.connection.commit()
                    return 'Password reset Successfull'
                else:
                    return 'Password mismatch'
            return render_template('newpassword.html')
        except Exception as e:
            print(e)
            return 'Link expired try again'
app.run(use_reloader=True,debug=True)



























