import datetime
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort

import stock_analysis.models
from stock_analysis import app, db, bcrypt
from stock_analysis.forms import RegistrationForm, LoginForm, UpdateAccountForm, AnalysisForm, StockForm, DiagramForm
from stock_analysis.models import User, Analysis, Stock, Diagram
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    stocks = Stock.query.order_by(Stock.name).all()
    analyses = []
    if current_user.is_authenticated:
        analyses = Analysis.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', stocks=stocks, analyses=analyses)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])  # this route can receive GET and POST requests
def register():
    if current_user.is_authenticated:  # if the user is already authenticated
        return redirect(url_for('home'))  # redirect the user to the home page
    form = RegistrationForm()  # instanciates a new form -- lecture 6
    if form.validate_on_submit():  # if the user submitted data and the data is validated
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # create a new instance of the class User -- lecture 6
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)  # adds the user to the database
        try:  # error handling
            # transaction management - databases
            # the changes to the database are only persisted once you commit the session
            db.session.commit()
            app.logger.debug('New user created successfully.')  # error handling
            flash('Your account has been created! You are now able to log in.', 'success')  # show message to user
            return redirect(url_for('login'))
        except Exception as e:
            # transaction management - databases
            # if something goes wrong with the transaction, you need to rollback the session
            db.session.rollback()
            app.logger.critical(f'Error while creating the user {user}')  # error handling
            app.logger.exception(e)  # error handling
            flash('The system encountered a problem while creating your account. Try again later.', 'danger')
    return render_template('register.html',
                           title='Register',
                           form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html',
                           title='Login',
                           form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_compressed_picture(form_picture):
    """
    Function that gets the file contained in the parameter `form_picture`, compresses it to a 125x125 pixels image,
    and saves it to the `static/profile_pics` folder.
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def save_raw_picture(form_picture):
    """
    Function that gets the file contained in the parameter `form_picture`,
    and saves it to the `static/profile_pics` folder.
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    form_picture.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            # (un)comment the lines below to get the desired effect
            # picture_file = save_compressed_picture(form.picture.data)  # this function saves a compressed picture
            picture_file = save_raw_picture(form.picture.data)  # this function saves the exact file
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        try:
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
        except Exception as e:
            db.session.rollback()
            app.logger.critical(f'Error while updating your account. {current_user}')
            app.logger.exception(e)
            flash('There was an error while updating your account. Try again later.', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html',
                           title='Account',
                           form=form)


@app.route("/stock/new", methods=['GET', 'POST'])
@login_required
def create_stock():
    form = StockForm()
    if form.validate_on_submit():
        created_stock = Stock(name=form.name.data.upper(),
                              number_of_shares=form.number_of_shares.data,
                              ticker=form.ticker.data.upper()
                              )
        db.session.add(created_stock)
        try:
            db.session.commit()
            flash('Your stock has been created!', 'success')
            return redirect(url_for('home'))
        except:
            flash('This stock is already created', 'danger')
            return redirect(url_for('create_stock'))

    return render_template('create_stock.html',
                           title='New Stock',
                           form=form,
                           legend='New Stock')


@app.route("/stock/<int:stock_id>/analysis", methods=['GET', 'POST'])
@login_required
def create_analysis(stock_id):
    form = AnalysisForm()
    current_stock = Stock.query.get_or_404(stock_id)
    if form.validate_on_submit():
        new_analysis = Analysis(title=form.title.data,
                                    content=form.content.data,
                                    price=form.price.data,
                                    earnings=form.earnings.data,
                                    p_e=form.p_e.data,
                                    market_cap=form.market_cap.data,
                                    user=current_user,
                                    stock=current_stock
                                    )
        db.session.add(new_analysis)
        try:
            db.session.commit()
            flash('Your analysis has been created!', 'success')
            return redirect(f'/stock/{current_stock.id}')
        except:
            flash('Something went wrong, please try again', 'danger')
            return redirect(url_for('create_analysis', stock_id=stock_id))

    return render_template('create_analysis.html',
                           stock=current_stock.id,
                           form=form,
                           legend='New Analysis')


@app.route("/stock/<int:stock_id>", methods=['GET', 'POST'])
def stock(stock_id):
    current_stock = Stock.query.get_or_404(stock_id)
    diagrams = []
    if 'startdate' in request.args and 'enddate' in request.args:
        startdate = datetime.datetime.strptime(request.args['startdate'], '%Y-%m-%d')
        enddate = datetime.datetime.strptime(request.args['enddate'], '%Y-%m-%d')
        diagrams = Diagram.query.filter_by(stock_id=current_stock.id).filter(Diagram.date >=startdate).filter(Diagram.date <= enddate).all()
    else:
        diagrams = Diagram.query.filter_by(stock_id=current_stock.id).order_by(Diagram.date).all()
    return render_template('stock.html',
                           stock=current_stock,
                           diagrams=diagrams
                           )

@app.route("/diagram/<int:stock_id>/new-price", methods=['GET', 'POST'])
@login_required
def add_price(stock_id):
    stock= Stock.query.get_or_404(stock_id)
    form = DiagramForm()
    if form.validate_on_submit():
        new_price = Diagram(price=form.price.data,
                            stock=stock)
        db.session.add(new_price)
        try:
            db.session.commit()
            flash('Your price has been added!', 'success')
            return redirect(f'/stock/{stock.id}')
        except:
            flash('Something went wrong, please try again', 'danger')
            return redirect(url_for('add_price'))

    return render_template('add_price.html',
                           title='Add Price',
                           form=form,
                           legend='Add Price'
                           )


@app.route("/analysis/<int:analysis_id>/", methods=['GET', 'POST'])
def analysis(analysis_id):
    current_analysis = Analysis.query.get_or_404(analysis_id)
    return render_template('analysis.html', analysis=current_analysis)


@app.route("/analysis/<int:analysis_id>/update", methods=['GET', 'POST'])
@login_required
def update_analysis(analysis_id):
    analysis_to_update = Analysis.query.get_or_404(analysis_id)
    if analysis_to_update.user != current_user:
        abort(403)  # only the owner of the post can edit it!
    form = AnalysisForm()
    if form.validate_on_submit():
        analysis_to_update.title = form.title.data
        analysis_to_update.content = form.content.data
        analysis_to_update.price = form.price.data
        analysis_to_update.earnings = form.earnings.data
        analysis_to_update.p_e = form.p_e.data
        analysis_to_update.market_cap = form.market_cap.data
        db.session.commit()
        flash('Your analysis has been updated!', 'success')
        return redirect(url_for('analysis', analysis_id=analysis_to_update.id))
    elif request.method == 'GET':
        form.title.data = analysis_to_update.title
        form.content.data = analysis_to_update.content
        form.price.data = analysis_to_update.price
        form.earnings.data = analysis_to_update.earnings
        form.p_e.data = analysis_to_update.p_e
        form.market_cap.data = analysis_to_update.market_cap

    return render_template('create_analysis.html',
                           title='Update Analysis',
                           form=form,
                           legend='Update Analysis')


@app.route("/analysis/<int:analysis_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_analysis(analysis_id):
    analysis_to_delete = Analysis.query.get_or_404(analysis_id)
    db.session.delete(analysis_to_delete)
    try:
        db.session.commit()
        flash('Your post has been deleted!', 'success')
        return redirect(url_for('home'))
    except:
        flash('It wasn??t possible to delete the analysis', 'danger')
    return redirect(url_for('stock', stock_id=analysis_to_delete.stock.id))


