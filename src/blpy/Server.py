'''
Created on 09.04.2012

@author: pyro
'''

from gzip import GzipFile
from io import BytesIO
from datetime import datetime

from twisted.internet import defer
from twisted.web import server
from twisted.web.resource import Resource

class outgoing_blacklist(Resource):
    isLeaf = True
    def __init__(self, name, incomming_lists):
        Resource.__init__(self)
        self.name = name
        self.incomming_lists = incomming_lists
        self.update_period = min([i.update_period for i in self.incomming_lists])
        self.last_update = None
        self.response = None
        self.dl = None

    def render(self, request):
        self.dl = defer.DeferredList([i.get_blocklist()
                                      for i in self.incomming_lists])
        self.dl.addCallback(self._render_callback, request)
        return server.NOT_DONE_YET

    def _render_callback(self, result, request):
        if (not self.last_update or
            not self.response or
            self.last_update + self.update_period < datetime.now()):
            self.response = BytesIO()
            self.last_update = datetime.now()
            f = GzipFile(mode='wb', fileobj=self.response)
            for (success, value) in result:
                if success:
                    f.write(value[1])
                else:
                    print('ERROR!')
            f.close()

        request.setHeader('Content-Encoding', 'gzip')
        request.setHeader('Content-Type', 'text/plain')
        request.setHeader('Accept-Ranges', 'bytes')

        request.write(self.response.getvalue())

        request.finish()

class list_resource(Resource):
    isLeaf = True

    header = '<!DOCTYPE html><html><head><title>{0}</title></head><body>' \
             '<h1>Available Blocklists:</h1><br/>'
    content = '<a href="{0}">{0}</a>'
    footer = '</body></html>'

    inc_title = '<h2>Incomming Lists:</h2>'
    out_title = '<h2>Outgoing Lists:</h2>'

    def __init__(self, title, outgoing_list_names, incomming_list_names):
        Resource.__init__(self)
        self.title = title
        self.outgoing_list_names = outgoing_list_names
        self.incomming_list_names = incomming_list_names

    def render(self, request):
        request.write(self.header.format(self.title))
        request.write(self.inc_title)
        request.write('<br/>'.join([self.content.format(c)
                                    for c in sorted(self.incomming_list_names)])
                      )
        request.write(self.out_title)
        request.write('<br/>'.join([self.content.format(c)
                                    for c in sorted(self.outgoing_list_names)])
                      )
        request.write(self.footer)
        request.finish()
        return server.NOT_DONE_YET

class root_resource(Resource):
    def __init__(self, outgoing_lists=list(), incomming_lists=list(),
                 title="Blocklist Merger"):
        Resource.__init__(self)
        out_list_names = []
        inc_list_names = []
        for l in outgoing_lists:
            name = 'out_' + l.name
            self.putChild(name, l)
            out_list_names.append(name)
        for l in incomming_lists:
            name = 'inc_' + l.name
            self.putChild(name, l)
            inc_list_names.append(name)
        self.putChild('', list_resource(title, out_list_names, inc_list_names))




