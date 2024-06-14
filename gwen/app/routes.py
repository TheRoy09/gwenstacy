from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, EmailLoginForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
import imaplib
import email
from email.header import decode_header

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/home")
@login_required
def home():
    return render_template('home.html')

@app.route("/get-emails", methods=['GET', 'POST'])
@login_required
def get_emails():
    form = EmailLoginForm()
    if form.validate_on_submit():
        email_user = form.email.data
        email_pass = form.password.data
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(email_user, email_pass)
            mail.select('inbox')

            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
            emails = []
            for email_id in email_ids[:10]:  # Fetch the latest 10 emails
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg['Subject'])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else 'utf-8')
                        from_ = msg.get('From')
                        emails.append({'subject': subject, 'from': from_})
            return render_template('emails.html', emails=emails)
        except Exception as e:
            print(str(e))
            flash('Error fetching emails', 'danger')
    return render_template('get_emails.html', title='Get Emails', form=form)