from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

class WebServerHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			if self.path.endswith('/hello'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""

				output += "<html><body>Hello!</body></html>"
				self.wfile.write(output)
				print output
				return 

			if self.path.endswith('/hola'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""

				output += "<html><body>Hola! <a href='/hello'>Back to hello</a></body></html>"
				self.wfile.write(output)
				print output
				return 

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)

	def do_POST(self):
		try:
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			

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