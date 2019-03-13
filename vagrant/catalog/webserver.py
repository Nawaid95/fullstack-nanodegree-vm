from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Database CRUD Setup
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurant") :
                rest_queryset = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                output = ""
                output += "<html><body><h2>Restaurants</h2>"
                # output += """<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like to say ? </h2>
                #     <input name='message' type='text'><input type='submit' value='Submit'></form>"""
                output += "<ul style='list-style-type:none;'>"
                for rest in rest_queryset :
                    output += """<li style='font-size:25px; padding-top:25px;'> %s </li>
                                <li><a href='/restaurant/%s/edit'> Edit </a></li>
                                <li><a href='/restaurant/%s/delete'> Delete </a></li>""" %(rest.name, rest.id, rest.id)
                output += "</ul><h4><a href='/restaurant/new'>Add New</a></h4></body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurant/new") :
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h2> Add Restaurant </h2>"
                output += """<form method='POST' enctype='multipart/form-data'>
                    <input name='restName' type='text'><input type='submit' value='Submit'></form>"""
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/edit") :
                restaurant_id = self.path.split('/')[2]

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                rest_obj = session.query(Restaurant).filter_by(id=restaurant_id).one()

                output = ""
                output += "<html><body>"
                output += "<h2>Edit %s</h2>" % rest_obj.name
                output += """<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/edit'>
                                <input name='newName' type='text'><input type='submit' value='Submit'></form>""" %rest_obj.id
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/delete") :
                restaurant_id = self.path.split('/')[2]

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                rest_obj = session.query(Restaurant).filter_by(id=restaurant_id).one()

                output = ""
                output += "<html><body>"
                output += "<h2>Are you sure to delete %s</h2>" % rest_obj.name
                output += """<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/delete'>
                                <input type='submit' value='Delete'></form>""" %rest_obj.id
                output += "</body></html>"
                self.wfile.write(output)
                return


            
        except IOError :
            self.send_error(404, "File not found %s" %self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/restaurant/new') :
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == "multipart/form-data":
                    fields=cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('restName')[0]

                print "######### %s" %messagecontent

                newRestaurant = Restaurant(name = messagecontent)
                session.add(newRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'html')
                self.send_header('Location', '/restaurant')
                self.end_headers()

                return

            if self.path.endswith("/edit") :
                restaurant_id = self.path.split('/')[2]
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == "multipart/form-data":
                    fields=cgi.parse_multipart(self.rfile, pdict)
                newName = fields.get('newName')[0]
                rest_obj = session.query(Restaurant).filter_by(id=restaurant_id).one()
                if rest_obj :
                    rest_obj.name = newName
                    session.add(rest_obj)
                    session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'html')
                self.send_header('Location', '/restaurant')
                self.end_headers()

            if self.path.endswith("/delete") :
                restaurant_id = self.path.split('/')[2]
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == "multipart/form-data":
                    fields=cgi.parse_multipart(self.rfile, pdict)
                rest_obj = session.query(Restaurant).filter_by(id=restaurant_id).one()
                if rest_obj :
                    session.delete(rest_obj)
                    session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'html')
                self.send_header('Location', '/restaurant')
                self.end_headers()
                

        
        except :
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running in port %s" %port
        server.serve_forever()

    except KeyboardInterrupt :
        print "^C entered, Stopping the server...."
        server.socket.close()

if __name__ == "__main__":
    main()