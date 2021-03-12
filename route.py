import os
from flask import Flask, render_template, flash, redirect, session, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from flask_mail import Mail, Message    
from threading import Thread
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)   

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///contactus.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] =  os.environ.get('SECRET_KEY')

app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT']= 587
app.config['MAIL_USE_TLS']= True
app.config['MAIL_USE_SSL']= False
app.config['MAIL_USERNAME']= os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']= os.environ.get('MAIL_PASSWORD')

mail=Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)

class contactus(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30))
    email = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    query = db.Column(db.String(100))

    def __repr__(self) -> str:
        return f"{self.id} - {self.name}"

class ContactUs(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    query = TextAreaField('Query', validators=[DataRequired()])
    submit = SubmitField('Submit' )

@app.route('/',methods=['GET', 'POST'])

    
def index():
    form= ContactUs()
    if request.method == 'POST':
        if form.validate_on_submit:
            name = form.name.data
            email = form.email.data
            subject = form.subject.data
            query = form.query.data

            contact=contactus(name= name, email= email, subject= subject, query= query)
            db.session.add(contact)
            db.session.commit()

            msg = Message(subject="[ADMIN]- New Query posted", sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body=f"New Query Posted-\nName: {name}\nE-Mail: {email}\n\nSubject: {subject}\nQuery: {query}"
            mail.send(msg)

            flash("Your query is successfully posted!")
            return redirect(url_for('index'))

    return render_template('index.html', form=form, name=session.get('name'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500   

if __name__ == '__main__':  
    app.run()