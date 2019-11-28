from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy.orm import sessionmaker 
from sqlalchemy import create_engine
from database_setup import Base, Restaurant, MenuItem, engine

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		try:

			if self.path.endswith('/restaurants'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""

				output += "<html><body>"
				"<h3><a href = '/restaurants/new'> Make A New Restaurant </a></h3>"

				our_restaurants = session.query(Restaurant).all()
				output += "<ul>"

				for restaurant in our_restaurants:
					
					output += "<li>" 
					output += "<h4>%s</h4>" % restaurant.name
					output += "<a href='restaurants/%s/edit'>Edit</a><br>" % restaurant.id
					output += "<a href='restaurants/%s/delete'>Delete</a>" % restaurant.id
				output += "</ul>"	
				output += '</body></html>'

				self.wfile.write(output)
				print output
				return 

			if self.path.endswith('/restaurants/new'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "<h1>Make a new Restaurant</h1>"

				output += '''
				<form method= "POST" enctype="multipart/form-data" 
				  action="/restaurants/new">

				  <input type="text" name="newRestaurantName"
				  	placeholder="New Restaurant Name">
			  	  <input type="submit" value="Create">
				</form>
				'''
				output += '</body></html>'

				self.wfile.write(output)
				print output
				return 

			if self.path.endswith('/edit'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				restaurant_id = int(self.path.split('/')[2])

				restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

				output = "<html><body>"
				output += "<h1>%s</h1>" % restaurant.name
				output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/edit' >" % restaurant_id
				output += "<input name = 'newRestaurantName' type='text' placeholder = '%s' >" % restaurant.name
				output += "<input type = 'submit' value = 'Rename'>"
				output += "</form></body></html>"

				self.wfile.write(output)
				print self.path
				return 


			if self.path.endswith('/delete'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				restaurant_id = int(self.path.split('/')[2])

				restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

				output = "<html><body>"
				output += '<h1>Are you sure to delete %s' % restaurant.name
				output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/delete' >" % restaurant_id
				output += "<input type = 'submit' value = 'Delete'>"
				output += "</form>"
				output += "<a href='/restaurants'>back</a>"
				output += "</body></html>"

				self.wfile.write(output)
				print self.path
				return


			

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)

	def do_POST(self):
		try:
			if self.path.endswith('restaurants/new'):
				
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					newRestaurantName  = fields.get('newRestaurantName')[0]

				
				newRestaurant = Restaurant(name = newRestaurantName)
				session.add(newRestaurant)
				session.commit()

				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()
				self.wfile.write(output)


				return


			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('newRestaurantName')
					restaurantIDPath = self.path.split("/")[2]

					myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
					if myRestaurantQuery != []:
						myRestaurantQuery.name = messagecontent[0]
						session.add(myRestaurantQuery)
						session.commit()
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()

			
			if self.path.endswith('/delete'):
				restaurant_id = self.path.split("/")[2]
				restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

				if restaurant != [] :
					session.delete(restaurant)
					session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()


		except:
			pass



def main():
	try:
		port = 8000
		server = HTTPServer(('', port), WebServerHandler)
		print "Web Server running on the port %s" %port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.close()

if __name__ == '__main__':
	main()