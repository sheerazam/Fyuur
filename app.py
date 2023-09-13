#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import render_template, request, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from forms import *
import sys
from models import app, db, Artist, Venue, Show
from utils import *

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  recent_artists = db.session.query(Artist).order_by(Artist.id.desc()).limit(10).all()
  recent_venues = db.session.query(Venue).order_by(Venue.id.desc()).limit(10).all()
  return render_template('pages/home.html', recent_artists=recent_artists, recent_venues=recent_venues)

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # (Done) replace with real venues data.

  areas = []

  result = (db.session.query(
                Venue.city,
                Venue.state
                )
        .distinct(Venue.city, Venue.state)
        .all())

  for i in result:
    area = {
      "city": i.city,
      "state": i.state
    }
    area['venues'] = db.session.query(Venue).filter(Venue.city == i.city, Venue.state == i.state).all()
    areas.append(area)
  return render_template('pages/venues.html', areas= areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # (Done) implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response = {
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term= search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # (Done) replace with real venue data from the venues table, using venue_id
  try:
    data = db.session.query(Venue).filter(Venue.id == venue_id).first()
    
    data.past_shows =  db.session.query(Show).join(Artist).filter(Show.c.venue_id == venue_id).filter(Show.c.artist_id == Artist.id).filter(Show.c.start_time <= datetime.now()).all()
    data.upcoming_shows =  db.session.query(Show).join(Artist).filter(Show.c.venue_id == venue_id).filter(Show.c.artist_id == Artist.id).filter(Show.c.start_time > datetime.now()).all()
    data.past_shows_count = len(data.past_shows)
    data.upcoming_shows_count = len(data.upcoming_shows)

  except:
    print(sys.exc_info())
    data = {}

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # (Done) insert form data as a new Venue record in the db, instead
  # (Done) modify data to be the data object returned from db insertion
  form = VenueForm(request.form)

  flashType = 'danger'

  if(form.validate()):
    try:
      venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data,
        genres=form.genres.data
      )
      db.session.add(venue)
      db.session.commit()
      flashType = 'success'
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      print(sys.exc_info())
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    flash(form.errors) 
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    
  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # (Done) on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html', flashType=flashType)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # (Done) Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    print(sys.exc_info())
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
    db.session.rollback()

  return venue

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # (Done) replace with real data returned from querying the database
  data = db.session.query(Artist).order_by(Artist.name).all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # (Done) implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  try:
    searchTerm = request.form.get('search_term', '')
    data = db.session.query(Artist).filter(Artist.name.ilike(f'%{searchTerm}%')).all()
    response = {
      "count": len(data),
      "data": data
    }
  except:
    print(sys.exc_info())
    response = []
  return render_template('pages/search_artists.html', results=response, search_term=searchTerm)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # (Done) replace with real artist data from the artist table, using artist_id
  data = db.session.query(Artist).filter(Artist.id == artist_id).first()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  # (Done) populate form with fields from artist with ID <artist_id>

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.seeking_venue = artist.seeking_venue
  form.seeking_description = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # (Done) take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  if(form.validate()):
    try:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = form.genres.data
      artist.facebook_link = form.facebook_link.data
      artist.image_link = form.image_link.data
      artist.seeking_description = form.seeking_description.data
      artist.seeking_venue = form.seeking_venue.data
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    flash(form.errors) 
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # (Done) populate form with values from venue with ID <venue_id>

  venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  form.name.data = venue.name
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # (Done) take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form)
  venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  if(form.validate()):
    try:
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.facebook_link = form.facebook_link.data
      venue.image_link = form.image_link.data
      venue.genres = form.genres.data
      venue.address = form.address.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    flash(form.errors) 
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # (Done) insert form data as a new Venue record in the db, instead
  # (Done) modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  if(form.validate()):
    try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      genres = form.genres.data
      facebook_link = form.facebook_link.data
      image_link = form.image_link.data
      genres = form.genres.data
      seeking_venue = form.seeking_venue.data
      seeking_description = form.seeking_description.data
      artist = Artist(name=name, 
        city=city, 
        state=state,
        phone=phone, 
        genres=genres,
        facebook_link=facebook_link, 
        image_link=image_link, 
        seeking_venue = seeking_venue, 
        seeking_description = seeking_description
      )
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      print(sys.exc_info())
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    flash(form.errors) 
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  
  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # (Done) on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # (Done) replace with real venues data.  
  data = (db.session.query(
    Venue.id.label("venue_id"), 
    Venue.name.label("venue_name"),
    Artist.id.label("artist_id"), 
    Artist.name.label("artist_name"), 
    Artist.image_link.label("artist_image_link"), 
    Show)
    .filter(Show.c.venue_id == Venue.id)
    .filter(Show.c.artist_id == Artist.id)
    .all())

  shows = list()
  i = 0
  for x in data:
    shows.append({
      "venue_id": x.venue_id,
      "venue_name": x.venue_name,
      "artist_id": x.artist_id,
      "artist_name": x.artist_name,
      "artist_image_link": x.artist_image_link,
      "start_time": format_datetime(x.start_time)
    })

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # (Done) insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  if(form.validate()):
    try:
      artist_id = form.artist_id.data
      venue_id = form.venue_id.data
      start_time = form.start_time.data
      show = Show.insert().values(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.execute(show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      print(sys.exc_info())
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
  else:
    flash(form.errors) 
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # (Done) on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
