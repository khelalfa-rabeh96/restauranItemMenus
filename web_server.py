from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy.orm import sessionmaker 
from database_setup import Base, Restaurant, MenuItem, engine

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
					
					output += "<li>%s</li>" % restaurant.name

				output += "</ul>"	
				output += '</body></html>'

				self.wfile.write(output)
				print output
				return 

			

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)

	def do_POST(self):
		try:

			self.send_response(301)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'multipart/form-data':
				fields = cgi.parse_multipart(self.rfile, pdict)
				message_content = fields.get('message')

			output = ""
			output += "<html><body>"
			output += "<h2> Okay, how about this: </h2>"
			output += "<h1> %s </h1>" % message_content[0]

			output += '''<form method="POST" enctype="multipart/form-data"
							action="/hello">
							<h2>What would you like me to say?</h2>
							<input name="message" type="text">
							<input type="submit" value="Submit">
						</form>'''
			output += '</body></html>'

			self.wfile.write(output)
			print output
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