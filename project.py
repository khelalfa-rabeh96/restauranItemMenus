from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

#New Imports for login step
from flask import session as login_session
import random, string


# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"




engine = create_engine('sqlite:///restaurantmenu.db?check_same_thread=False')
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
session = DBsession()


@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	print 'the current session state is %s' % login_session['state']
	return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"

    user_id = getUserID(login_session['email'])
    if not user_id :
    	user_id = createUser(user_id)

	login_session['user_id'] = user.id



    return output# Validate state token
    

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response






@app.route('/')
@app.route('/restaurants')
def showRestaurants():
	
	all_restaurants = session.query(Restaurant).all()
	return render_template('restaurants.html', all_restaurants = all_restaurants)

#Making an API Endpoint
@app.route('/restaurants/JSON')
def restaurantsJSON():
	all_restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants = [restaurant.serialize for restaurant in all_restaurants])


@app.route('/restaurants/new', methods=['GET', 'POST'])
def newRestaurant():
	if 'username' not in login_session:
		return redirect('/login')

	if request.method == 'POST':
		name = request.form['name']
		user_id = login_session['user_id']
		restaurant = Restaurant(name = name, user_id = user_id)
		session.add(restaurant)
		session.commit()
		flash('New Restaurant  %s  Successfuly Created' % restaurant.name)
		return redirect(url_for('showRestaurants'))

	else:
		return render_template('new_restaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login')

	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

	if request.method == 'POST':
		name = request.form['name']
		if name:
		
			restaurant.name = name
			session.add(restaurant)
			session.commit()
			flash('A Restaurant Edited Successfuly %s' % restaurant.name)

		return redirect(url_for('showRestaurants'))

	else:
		return render_template('editRestaurant.html', restaurant = restaurant)

@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login')

	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	
	if request.method == 'POST':
		session.delete(restaurant)
		session.commit()
		flash('%s Deleted Successfuly' % restaurant.name)
		return redirect(url_for('showRestaurants'))

	else:
		return render_template('deleteRestaurant.html', restaurant = restaurant)



#Making an API Endpoint
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id ).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return jsonify(MeuItems = [item.serialize for item in items])

@app.route('/restaurants/<int:restaurant_id>')
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()

	return render_template('menu.html', restaurant = restaurant, items = items)


#Making an API Endpoint
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
	item = session.query(MenuItem).filter_by(restaurant_id = restaurant_id, id = menu_id).one()
	return jsonify(MeuItem = item.serialize )



@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	if request.method == 'POST':
		

		name = request.form['name']
		description = request.form['description']
		price = request.form['price']
		course = request.form['course']
		newItem = MenuItem(name = name, description = description, price= price,
		 course = course ,restaurant_id = restaurant_id)
		session.add(newItem)
		session.commit()
		flash('new menu %s item created!' % newItem)
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))

	else:
		return render_template('newMenuItem.html', restaurant_id = restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenu(restaurant_id, menu_id):
	
	editedItem = session.query(MenuItem).filter_by(id= menu_id).one()
	
	if request.method == "POST":
		if request.form['name']:
		    editedItem.name = request.form['name']
		if request.form['description']:
		    editedItem.description = request.form['description']
		if request.form['price']:
		    editedItem.price = request.form['price']
		if request.form['course']:
		    editedItem.course = request.form['course']
		    

		session.add(editedItem)
		session.commit()
		flash('a menu item has  edited!')
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))

	else:
		return render_template('editMenuItem.html', restaurant_id = restaurant_id, item = editedItem)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenu(restaurant_id, menu_id):
	
	deletedItem = session.query(MenuItem).filter_by(id = menu_id ).one()
	if request.method == 'POST':	
		session.delete(deletedItem)
		session.commit()
		flash('a menu item has deleted!')
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))

	else:
		return render_template('deleteMenuItem.html',restaurant_id =restaurant_id, item = deletedItem)
	


def createUser(login_session):
	name = login_session['username']
	email = login_session['email']
	picture = login_session['picture']
	newUser = User(name=name, email=email, picture=picture)

	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email = email).one()
	return user.id

def getUserID(email):
	try:
		user = session.query(User).filter_by(email = email).one()
		return user.id
	except:
		return None
def getUserInfo(user_id):
	user = session.query(User).filter_by(id = user_id)
	return user


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)

