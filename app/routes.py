from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from app.forms import RegistrationForm, LoginForm, EditProfileForm, GigForm, CategoryForm, MessageForm
from app.models import User, Gig, Category
from werkzeug.urls import url_parse
from datetime import datetime



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()



@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')



@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))





@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        # Handle form submission (e.g., send a message)
        flash('Your message has been sent!')
        return redirect(url_for('user', username=user.username))
    return render_template('user.html', user=user, form=form)



@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/create_gig', methods=['GET', 'POST'])
@login_required
def create_gig():
    form = GigForm()
    if form.validate_on_submit():
        gig = Gig(
            seller=current_user,
            title=form.title.data,
            description=form.description.data,
            price=float(form.price.data),
            location=form.location.data,
            travel_radius=float(form.travel_radius.data),
            category=form.category.data
        )
        db.session.add(gig)
        db.session.commit()
        flash('Your gig has been created!')
        return redirect(url_for('user', username=current_user.username))
    return render_template('create_gig.html', title='Create Gig', form=form)



@app.route('/gig/<int:gig_id>')
def gig_detail(gig_id):
    gig = Gig.query.get_or_404(gig_id)
    return render_template('gig_detail.html', gig=gig)



@app.route('/edit_gig/<int:gig_id>', methods=['GET', 'POST'])
@login_required
def edit_gig(gig_id):
    gig = Gig.query.get_or_404(gig_id)
    if gig.seller != current_user:
        flash('You are not authorized to edit this gig.')
        return redirect(url_for('index'))
    form = GigForm()
    if form.validate_on_submit():
        gig.title = form.title.data
        gig.description = form.description.data
        gig.category = form.category.data
        gig.price = float(form.price.data)
        gig.location = form.location.data
        gig.travel_radius = float(form.travel_radius.data)
        db.session.commit()
        flash('Your gig has been updated.')
        return redirect(url_for('gig_detail', gig_id=gig.id))
    elif request.method == 'GET':
        form.title.data = gig.title
        form.description.data = gig.description
        form.category.data = gig.category
        form.price.data = str(gig.price)
        form.location.data = gig.location
        form.travel_radius.data = str(gig.travel_radius)
    return render_template('edit_gig.html', title='Edit Gig', form=form)



@app.route('/delete_gig/<int:gig_id>', methods=['POST'])
@login_required
def delete_gig(gig_id):
    gig = Gig.query.get_or_404(gig_id)
    if gig.seller != current_user:
        flash('You are not authorized to delete this gig.')
        return redirect(url_for('index'))
    db.session.delete(gig)
    db.session.commit()
    flash('Your gig has been deleted.')
    return redirect(url_for('user', username=current_user.username))



@app.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        existing_category = Category.query.filter_by(name=form.name.data).first()
        if existing_category:
            flash('Category already exists.')
            return redirect(url_for('create_gig'))
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('New category added.')
        return redirect(url_for('create_gig'))
    return render_template('add_category.html', title='Add Category', form=form)


