import os
import sys
import random
import datetime
import requests
from stock_analysis import db, bcrypt, app
from stock_analysis.models import User, Analysis, Stock, Diagram
from lorem_text import lorem
import string

host = 'localhost'  # host where the system is running
port = 5000  # port where the process is running

def reload_database():
    exit_reload = False
    try:
        response = requests.get(f'http://{host}:{port}')
        app.logger.critical('The website seems to be running. Please stop it and run this file again.')
        exit_reload = True
    except:
        pass
    if exit_reload:
        exit(11)
    try:
        os.remove('stock_analysis/site.db')
        app.logger.info('previous DB file removed')
    except:
        app.logger.info('no previous DB file found')

    assert not os.path.exists(
        'stock_analysis/site.db'), 'It seems that site.db was not deleted. Please delete it manually!'

    db.create_all()

    # creating two users
    hashed_password = bcrypt.generate_password_hash('testing').decode('utf-8')
    default_user1 = User(username='Default',
                         email='default@test.com',
                         image_file='another_pic.jpeg',
                         password=hashed_password)
    db.session.add(default_user1)

    hashed_password = bcrypt.generate_password_hash('testing2').decode('utf-8')
    default_user2 = User(username='Default Second',
                         email='second@test.com',
                         image_file='7798432669b8b3ac.jpg',
                         password=hashed_password)
    db.session.add(default_user2)

    hashed_password = bcrypt.generate_password_hash('testing3').decode('utf-8')
    default_user3 = User(username='Default Third',
                         email='third@test.com',
                         password=hashed_password)
    db.session.add(default_user3)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.critical('Error while committing the user insertion.')
        app.logger.exception(e)

    # testing if the users were added correctly

    def random_char(y):
        return ''.join(random.choice(string.ascii_letters) for x in range(y))

    assert len(User.query.all()) == 3, 'It seems that user failed to be inserted!'
    users = [default_user1, default_user2, default_user3]

    stock_1 = Stock(name='INVESTOR', number_of_shares=random.randint(1, 100000), ticker=random_char(4).upper())
    db.session.add(stock_1)

    stock_2 = Stock(name='HELLO', number_of_shares=random.randint(1, 1000000), ticker=random_char(4).upper())
    db.session.add(stock_2)

    stock_3 = Stock(name='NIBE', number_of_shares=random.randint(1, 1000000), ticker=random_char(4).upper())
    db.session.add(stock_3)

    stocks = [stock_1, stock_2, stock_3]

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        app.logger.critical('Error while committing the user insertion.')
        app.logger.exception()

    for stock in stocks:
        for user in users:
            for a in range(random.randint(1, 10)):
                # picking a random date for the analysis
                random_date = datetime.datetime.now() - \
                                datetime.timedelta(days=random.randint(1, 90),
                                                   hours=random.randint(1, 23),
                                                   minutes=random.randint(1, 59))
                # creating a random analysis
                analysis = Analysis(title=lorem.words(random.randint(3, 10)),
                                    content=lorem.words(random.randint(3, 20)),
                                    date_posted=random_date,
                                    price=random.randint(1, 1000),
                                    earnings=random.randint(1, 100000),
                                    p_e=random.randint(-5, 20),
                                    market_cap=random.randint(1, 10000),
                                    user=user,
                                    stock=stock)
                db.session.add(analysis)

                diagram = Diagram(date=random_date, stock=stock, price=random.randint(1,1000))
                db.session.add(diagram)

    try:
        db.session.commit()
        app.logger.info('Finalized - database created successfully!')
    except Exception as e:
        db.session.rollback()
        app.logger.critical('The operations were not successful.')
        app.logger.exception(e)


def query_database():
    # listing all the users
    users = User.query.all()
    print('\nAll users:')
    for user in users:
        print('\t', user)

    stocks = Stock.query.all()
    print('\nAll stocks:')
    for stock in stocks:
        print('\t', stock)

    analyses = Analysis.query.all()
    print('\nAll analyses:')
    for analysis in analyses:
        print('\t', analysis)

    diagrams = Diagram.query.all()
    print('\nAll diagrams:')
    for diagram in diagrams:
        print('\t', diagram)


if __name__ == '__main__':
    reload_database()
    query_database()
