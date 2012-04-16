'''
Created on 09.04.2012

@author: pyro
'''

from datetime import datetime, timedelta

from gzip import GzipFile
from io import BytesIO
frgz = lambda value: GzipFile(fileobj=BytesIO(value)).read()

import re

from twisted.internet import defer
from twisted.web import server
from twisted.web.client import getPage
from twisted.web.resource import Resource

Comment_re = re.compile('^#.*$', re.M)
Emptyline_re = re.compile('[\n\r]+(?:\s*[\n\r]*)*')

class incomming_blacklist(Resource):
    isLeaf = True
    def __init__(self, name, url, update_days):
        Resource.__init__(self)
        self.name = name
        self.url = url
        self.update_period = timedelta(update_days)
        self.last_update = None
        self.blocklist = None

        self.d = None

    def _get_blocklist_callback(self, value):
        self
        self.blocklist = frgz(value)
        self.blocklist = Comment_re.sub('', self.blocklist)
        self.blocklist = Emptyline_re.sub('\n', self.blocklist)

        self.last_update = datetime.now()

        return value, self.blocklist

    def _render_callback(self, value, request):
        request.setHeader('Content-Encoding', 'gzip')
        request.setHeader('Content-Type', 'text/plain')
        request.setHeader('Accept-Ranges', 'bytes')

        request.write(value[0])

        request.finish()

    def get_blocklist(self):
        if (not self.last_update or
            not self.blocklist or
            self.last_update + self.update_period < datetime.now()):

            page = getPage(self.url)
            page.addCallback(self._get_blocklist_callback)
            return page
        else:
            return defer.succeed(self.blocklist)

    def render(self, request):
        self.get_blocklist().addCallback(self._render_callback, request)
        return server.NOT_DONE_YET
