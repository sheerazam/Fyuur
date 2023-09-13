
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # (Done) implement any missing fields, as a database migration using Flask-Migrate
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    genres = db.Column(db.ARRAY(db.String()))
    seeking_description = db.Column(db.String(500)) 
    venues = db.relationship('Artist', secondary='Show', backref=db.backref('shows', lazy='joined'))

    def __repr__(self):
        return 'Venue id:{}, name: {}'.format(self.id, self.name)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # (Done) implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    genres = db.Column(db.ARRAY(db.String()))
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
        return 'Artist Id:{}, Name: {}'.format(self.id, self.name)

# (Done) Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

Show = db.Table('Show', db.Model.metadata,
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id')),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id')),
    db.Column('start_time', db.DateTime)
)