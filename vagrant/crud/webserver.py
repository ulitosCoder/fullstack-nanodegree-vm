from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine,  desc, asc, Date
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem
import cgi


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Hello!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
                

            if self.path.endswith("/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                #output += "you'll be adding a new place herrrre!</br>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h3>Restaurant name</h3><input name="newName" type="text" ><input type="submit" value="Submit">         </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                
                output += "<a href='/restaurants/new'> Add new Restaurant herrrre </a>"
                query1 = session.query(Restaurant).order_by(asc(Restaurant.name)).all()
                for item in query1:
                    output += '<p>%s</p>' % item.name
                    output += '<a href="%s/edit">Edit %s</a></br>' % (item.id,item.name)
                    output += '<a href="#"">Delete %s</a></br>' % item.name
                    output += '</br>'
                    print item.name #, ', ',  item.dateOfBirth

                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            print 'ioerror'
            self.send_error(404, 'File Not Found: %s' % self.path)
            
        except:
            print 'other error'
            self.send_error(500, 'Internal Server Error')



    def do_POST(self):
        try:
            output = ""
            output += "<html><body>"
            
            if self.path.endswith("/hello"):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                    output += " <h2> OK, how about this: </h2>"
                    output += "<h1> %s </h1>" % messagecontent[0]
                    output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''


            if self.path.endswith("/restaurants/new"):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newName')
                
                newPlace = Restaurant(name=messagecontent[0])
                session.add(newPlace)
                session.commit()

                output += " <h2> New place added: </h2>"
                output += "<h1> %s </h1>" % messagecontent[0]
                output += "</br>"
                output += '<a href="/restaurants">Go to list</a></br>'

                
                

            output += "</body></html>"
            self.wfile.write(output)
            #print output
        except:
            print 'other error'
            self.send_error(500, 'Internal Server Error')
            pass


def main():
    try:
        port = 8081
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()