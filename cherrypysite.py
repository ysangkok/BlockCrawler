#!/usr/bin/env python3.3
import block_crawler
import cherrypy
from cgi import MiniFieldStorage
import os.path
 
class HelloWorld(object):
    def index(self, **kwargs):
        a = block_crawler.main(dict([(x, MiniFieldStorage(x,y)) for x,y in kwargs.items()]))
        return "".join(a)
    index.exposed = True
 
cherrypy.quickstart(HelloWorld(), '/', config={'/': {'response.stream': False}, '/block_crawler.css' : {'tools.staticfile.on' : True, 'tools.staticfile.filename': os.path.abspath('block_crawler.css')}}) #, '/static': {'tools.staticdir.dir': ".", "tools.staticdir.on": True}}

