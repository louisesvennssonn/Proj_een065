"""
This file contains the declarations of the models.
"""
from dataclasses import dataclass
import datetime
from stock_analysis import db, login_manager
from flask_login import UserMixin



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@dataclass
class User(db.Model, UserMixin):
    id: int
    username: str
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}', image_file='{self.image_file}')>"


@dataclass
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    number_of_shares = db.Column(db.Integer, nullable=False)
    ticker = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"<Stock(id='{self.id}', name='{self.name}', number_of_shares='{self.number_of_shares}', ticker='{self.ticker}')>"


@dataclass
class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    price = db.Column(db.Float, nullable=False)
    earnings = db.Column(db.Float, nullable=False)
    p_e = db.Column(db.Float, nullable=False)
    market_cap = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, backref=db.backref('analyses', lazy=True))

    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    stock = db.relationship(Stock, backref=db.backref('analyses', lazy=True, order_by='Analysis.date_posted.desc()'))

    def __repr__(self):
        return f"<Analysis(id='{self.id}', stock_id='{self.stock_id}', user_id='{self.user_id}', date_posted='{self.date_posted}', price='{self.price}', earnings='{self.earnings}', p_e='{self.p_e}')>"


@dataclass
class Diagram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    price = db.Column(db.Float, nullable=False)

    stock = db.relationship(Stock, backref=db.backref('diagrams'), lazy=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)

    def __repr__(self):
        return f"<Diagram(date='{self.date}', price='{self.price}', stock='{self.stock_id}')>"