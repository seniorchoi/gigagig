from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from app.forms import RegistrationForm, LoginForm, EditProfileForm, GigForm, CategoryForm, MessageForm, ReviewForm, SearchForm, BookingForm, EmptyForm
from app.models import User, Gig, Category, Message, Review, Booking
from werkzeug.urls import url_parse
from datetime import datetime
import os
from PIL import Image



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



def save_picture(form_picture):
    random_hex = os.urandom(8).hex()
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    # Resize the image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            picture_file = save_picture(form.profile_picture.data)
            current_user.profile_image = picture_file
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



@app.route('/gig/<int:gig_id>', methods=['GET', 'POST'])
def gig_detail(gig_id):
    gig = Gig.query.get_or_404(gig_id)
    form = EmptyForm()
    return render_template('gig_detail.html', gig=gig, form=form)



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



@app.route('/send_message/<username>', methods=['GET', 'POST'])
@login_required
def send_message(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(sender=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('user', username=username))
    return render_template('send_message.html', form=form, recipient=user)



@app.route('/messages')
@login_required
def messages():
    messages = current_user.received_messages.order_by(Message.timestamp.desc()).all()
    return render_template('messages.html', messages=messages)



@app.route('/book/<int:gig_id>', methods=['GET', 'POST'])
@login_required
def book(gig_id):
    gig = Gig.query.get_or_404(gig_id)
    form = BookingForm()
    if form.validate_on_submit():
        booking = Booking(
            gig=gig,
            buyer=current_user,
            booking_date=form.booking_date.data
        )
        db.session.add(booking)
        db.session.commit()
        flash('Your booking request has been sent!')
        return redirect(url_for('booking_detail', booking_id=booking.id))
    return render_template('book.html', form=form, gig=gig)



@app.route('/booking/<int:booking_id>')
@login_required
def booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.buyer != current_user and booking.gig.seller != current_user:
        flash('You are not authorized to view this booking.')
        return redirect(url_for('index'))
    return render_template('booking_detail.html', booking=booking)



@app.route('/confirm_booking/<int:booking_id>', methods=['POST'])
@login_required
def confirm_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.gig.seller != current_user:
        flash('You are not authorized to confirm this booking.')
        return redirect(url_for('index'))
    booking.status = 'Confirmed'
    db.session.commit()
    flash('Booking confirmed!')
    return redirect(url_for('booking_detail', booking_id=booking.id))



@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    gigs = []
    if form.validate_on_submit():
        query = Gig.query
        if form.keyword.data:
            query = query.filter(Gig.title.ilike(f"%{form.keyword.data}%") | Gig.description.ilike(f"%{form.keyword.data}%"))
        if form.category.data:
            query = query.filter_by(category=form.category.data)
        if form.location.data:
            query = query.filter(Gig.location.ilike(f"%{form.location.data}%"))
        gigs = query.all()
    return render_template('search.html', form=form, gigs=gigs)



@app.route('/review/<int:gig_id>', methods=['GET', 'POST'])
@login_required
def review_gig(gig_id):
    gig = Gig.query.get_or_404(gig_id)
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            gig=gig,
            user=current_user,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted.')
        return redirect(url_for('gig_detail', gig_id=gig.id))
    return render_template('review.html', form=form, gig=gig)



@app.route('/my_gigs')
@login_required
def my_gigs():
    gigs = current_user.gigs.order_by(Gig.timestamp.desc()).all()
    return render_template('my_gigs.html', gigs=gigs)



@app.route('/my_bookings')
@login_required
def my_bookings():
    # Bookings where the user is the buyer
    bookings = Booking.query.filter_by(buyer_id=current_user.id).order_by(Booking.timestamp.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)



