from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from app.forms import RegistrationForm, LoginForm, EditProfileForm, GigForm, CategoryForm, MessageForm, ReviewForm, SearchForm, BookingForm, EmptyForm
from app.models import User, Gig, Category, Message, Review, Booking
from werkzeug.urls import url_parse
from datetime import datetime
import os
from PIL import Image
import stripe
import requests
from math import radians, cos, sin, asin, sqrt
from app.email import send_email





@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()



@app.context_processor
def inject_google_maps_key():
    return dict(GOOGLE_MAPS_API_KEY=current_app.config['GOOGLE_MAPS_API_KEY'])



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
        # Geocode the location
        address = form.location.data
        api_key = current_app.config['GOOGLE_MAPS_API_KEY']
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
        response = requests.get(geocode_url)
        data = response.json()
        if data['status'] == 'OK':
            location_data = data['results'][0]['geometry']['location']
            latitude = location_data['lat']
            longitude = location_data['lng']
        else:
            flash('Could not geocode the provided address.')
            return render_template('create_gig.html', title='Create Gig', form=form)

        gig = Gig(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            location=address,
            latitude=latitude,
            longitude=longitude,
            travel_radius=form.travel_radius.data,
            seller=current_user
        )
        db.session.add(gig)
        db.session.commit()
        flash('Your gig has been created!')
        return redirect(url_for('gig_detail', gig_id=gig.id))
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

        # Send email notification to the recipient
        subject = f'New message from {current_user.username}'
        html_content = render_template('email/new_message.html', user=user, message=msg)
        send_email(user.email, subject, html_content)

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
def book_gig(gig_id):
    gig = Gig.query.get_or_404(gig_id)
    form = BookingForm()
    if form.validate_on_submit():
        booking = Booking(
            gig=gig,
            buyer=current_user,
            booking_date=form.booking_date.data,
            status='Pending'
        )
        db.session.add(booking)
        db.session.commit()
        flash('Your booking request has been sent!')
        return redirect(url_for('booking_detail', booking_id=booking.id))
    return render_template('book_gig.html', title='Book Gig', form=form, gig=gig)



@app.route('/booking/<int:booking_id>')
@login_required
def booking_detail(booking_id):
    form = EmptyForm()
    booking = Booking.query.get_or_404(booking_id)
    if booking.buyer != current_user and booking.gig.seller != current_user:
        flash('You are not authorized to view this booking.')
        return redirect(url_for('index'))
    return render_template('booking_detail.html', booking=booking, form=form, Review=Review)



@app.route('/booking/<int:booking_id>/update_status', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.gig.seller != current_user:
        flash('You are not authorized to update this booking.')
        return redirect(url_for('index'))

    if booking.status != 'Pending':
        flash('You can only update pending bookings.')
        return redirect(url_for('booking_detail', booking_id=booking.id))

    action = request.form.get('action')
    if action == 'Accept':
        booking.status = 'Accepted'
        # Send email to buyer
        subject = 'Your booking has been accepted!'
        html_content = render_template('email/booking_accepted.html', booking=booking)
        send_email(booking.buyer.email, subject, html_content)
    elif action == 'Decline':
        booking.status = 'Declined'
        # Notify buyer that booking has been declined
    db.session.commit()
    flash(f'Booking has been {booking.status.lower()}.')
    return redirect(url_for('booking_detail', booking_id=booking.id))



@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        keyword = form.keyword.data
        category = form.category.data
        location = form.location.data
        return redirect(url_for('search_results', keyword=keyword, category_id=category.id if category else None, location=location))
    return render_template('search.html', title='Search Gigs', form=form)



def haversine(lon1, lat1, lon2, lat2):
    # Calculate the great circle distance between two points
    # on the earth (specified in decimal degrees)
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c  # Radius of earth in kilometers
    return km



@app.route('/search_results')
def search_results():
    keyword = request.args.get('keyword', '')
    category_id = request.args.get('category_id', type=int)
    location = request.args.get('location', '')
    radius = request.args.get('radius', type=int)

    query = Gig.query

    # Filter by keyword
    if keyword:
        query = query.filter(
            Gig.title.ilike(f'%{keyword}%') |
            Gig.description.ilike(f'%{keyword}%')
        )

    # Filter by category
    if category_id:
        query = query.filter_by(category_id=category_id)

    gigs = query.all()

    # Filter by proximity
    if location and radius:
        # Geocode user's location
        address = location
        api_key = current_app.config['GOOGLE_MAPS_API_KEY']
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
        response = requests.get(geocode_url)
        data = response.json()
        if data['status'] == 'OK':
            user_location = data['results'][0]['geometry']['location']
            user_lat = user_location['lat']
            user_lon = user_location['lng']

            # Filter gigs within radius
            nearby_gigs = []
            for gig in gigs:
                if gig.latitude and gig.longitude:
                    distance = haversine(user_lon, user_lat, gig.longitude, gig.latitude)
                    if distance <= radius:
                        nearby_gigs.append(gig)
            gigs = nearby_gigs
        else:
            flash('Could not geocode the provided location.')
            gigs = []
    else:
        gigs = query.all()

    return render_template('search_results.html', gigs=gigs, keyword=keyword, location=location)



@app.route('/review/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def review(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.buyer != current_user:
        flash('You are not authorized to review this gig.')
        return redirect(url_for('index'))
    # Check if the booking is completed
    if booking.status != 'Completed':
        flash('You can only review completed bookings.')
        return redirect(url_for('index'))
    # Check if a review already exists for this booking
    if booking.review is not None:
        flash('You have already reviewed this booking.')
        return redirect(url_for('gig_detail', gig_id=booking.gig_id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            gig=booking.gig,
            booking=booking,
            user=current_user,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted.')
        return redirect(url_for('gig_detail', gig_id=booking.gig_id))
    return render_template('review.html', form=form, gig=booking.gig)



@app.route('/complete_booking/<int:booking_id>', methods=['POST'])
@login_required
def complete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.gig.seller != current_user:
        flash('You are not authorized to complete this booking.')
        return redirect(url_for('index'))

    if booking.status != 'Confirmed':
        flash('Only confirmed bookings can be marked as completed.')
        return redirect(url_for('booking_detail', booking_id=booking.id))

    booking.status = 'Completed'
    db.session.commit()
    flash('Booking marked as completed.')
    # Notify buyer that booking is completed
    return redirect(url_for('booking_detail', booking_id=booking.id))



@app.route('/my_gigs')
@login_required
def my_gigs():
    gigs = current_user.gigs.order_by(Gig.timestamp.desc()).all()
    return render_template('my_gigs.html', gigs=gigs)



@app.route('/my_bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(buyer_id=current_user.id).order_by(Booking.timestamp.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)



@app.route('/bookings_for_my_gigs')
@login_required
def bookings_for_my_gigs():
    gigs = current_user.gigs.all()
    bookings = Booking.query.filter(Booking.gig_id.in_([gig.id for gig in gigs])).order_by(Booking.timestamp.desc()).all()
    return render_template('bookings_for_my_gigs.html', bookings=bookings)



@app.route('/create-checkout-session/<int:booking_id>', methods=['POST'])
@login_required
def create_checkout_session(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.buyer != current_user:
        flash('You are not authorized to make this payment.')
        return redirect(url_for('index'))
    
    if booking.status != 'Accepted':
        flash('Payment can only be made for accepted bookings.')
        return redirect(url_for('booking_detail', booking_id=booking.id))
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(booking.gig.price * 100),  # Amount in cents
                'product_data': {
                    'name': booking.gig.title,
                    'description': booking.gig.description,
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('payment_success', booking_id=booking.id, _external=True),
        cancel_url=url_for('booking_detail', booking_id=booking.id, _external=True),
    )
    return redirect(session.url, code=303)



@app.route('/payment_success/<int:booking_id>')
@login_required
def payment_success(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.buyer != current_user:
        flash('You are not authorized to access this page.')
        return redirect(url_for('index'))

    booking.status = 'Confirmed'
    db.session.commit()
    flash('Payment successful! Your booking is confirmed.')
    # Notify seller that booking has been confirmed
    return redirect(url_for('booking_detail', booking_id=booking.id))



