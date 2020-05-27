#!/usr/bin/env python

# Run this with
# PYTHONPATH=. DJANGO_SETTINGS_MODULE=testsite.settings testsite/tornado_main.py

from tornado.options import options, define, parse_command_line
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
import os
from django.utils import simplejson
from website.models import TextbookCompanionExampleDependency, TextbookCompanionDependencyFiles

from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from instances import ScilabInstance
import threading

define('port', type=int, default=8080)

# Custom settings
from soc.settings import PROJECT_DIR
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soc.settings")

DEFAULT_WORKERS = 5
request_count = 0

executor = ThreadPoolExecutor(max_workers = DEFAULT_WORKERS)

scilab_executor = ScilabInstance()
scilab_executor.spawn_instance()

def instance_manager():
  if(scilab_executor.count > request_count):
    scilab_executor.kill_instances(scilab_executor.count-request_count-1)
  threading.Timer(300, instance_manager).start()
  
instance_manager()

class ExecutionHandler(tornado.web.RequestHandler):
	@gen.coroutine
	def post(self):
		global request_count
		request_count += 1
		token = buffer(self.request.arguments['token'][0])
		token = str(token)
		code =  buffer(self.request.arguments['code'][0])
		code = str(code)
		book_id = int(self.request.arguments['book_id'][0])
		chapter_id = int(self.request.arguments['chapter_id'][0])
		example_id = int(self.request.arguments['example_id'][0])
		dependency_exists = TextbookCompanionExampleDependency.objects.using('scilab')\
			.filter(example_id=example_id).exists()
		data  = yield executor.submit(scilab_executor.execute_code, code, token, book_id, dependency_exists)
		self.write(data)
		request_count -= 1


def main():
  parse_command_line()
  wsgi_app = tornado.wsgi.WSGIContainer(
    get_wsgi_application())
  tornado_app = tornado.web.Application(
    [
      ('/execute-code', ExecutionHandler),
      ('/static/(.*)', tornado.web.StaticFileHandler, {'path': PROJECT_DIR + '/static/'}),
      ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
      ], debug=False)
  server = tornado.httpserver.HTTPServer(tornado_app)
  server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
  main()