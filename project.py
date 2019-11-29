from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db?check_same_thread=False')
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
session = DBsession()

@app.route('/')
@app.route('/restaurants')
def showRestaurants():
	
	all_restaurants = session.query(Restaurant).all()
	return render_template('restaurants.html', all_restaurants = all_restaurants)

@app.route('/restaurants/new', methods=['GET', 'POST'])
def newRestaurant():
	if request.method == 'POST':
		name = request.form['name']
		
		restaurant = Restaurant(name = name)
		session.add(restaurant)
		session.commit()
		return redirect(url_for('showRestaurants'))

	else:
		return render_template('new_restaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

	if request.method == 'POST':
		name = request.form['name']
		if name:
		
			restaurant.name = name
			session.add(restaurant)
			session.commit()

		return redirect(url_for('showRestaurants'))

	else:
		return render_template('editRestaurant.html', restaurant = restaurant)

@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	
	if request.method == 'POST':
		session.delete(restaurant)
		session.commit()

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
		newItem = MenuItem(name = request.form['name'], 
			restaurant_id = restaurant_id)

		session.add(newItem)
		session.commit()
		flash('new menu item created!')
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))

	else:
		return render_template('newMenuItem.html', restaurant_id = restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenu(restaurant_id, menu_id):
	
	editedItem = session.query(MenuItem).filter_by(id= menu_id).one()
	
	if request.method == "POST":
		if request.form['name']:
			editedItem.name = request.form['name']

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
	


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)

