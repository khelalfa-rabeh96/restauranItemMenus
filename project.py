from flask import Flask, render_template, url_for
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db?check_same_thread=False')
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
session = DBsession()

@app.route('/')
@app.route('/hello')
def HelloWorld():
	return "Hello World"

@app.route('/restaurants/<int:restaurant_id>')
def restauranMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()

	return render_template('menu.html', restaurant = restaurant, items = items)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit')
def editMenu(restaurant_id, menu_id):
	return "You want to edit this menu"

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete')
def deleteMenu(restaurant_id, menu_id):
	return "You want to delete this menu"


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)

