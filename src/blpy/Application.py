'''
Created on 09.04.2012

@author: pyro
'''

from ConfigParser import SafeConfigParser

from twisted.internet import reactor
from twisted.web import server

from Client import incomming_blacklist
from Server import outgoing_blacklist, root_resource

def StartServer(configfilepath):
    config = SafeConfigParser(allow_no_value=True)
    config.read(configfilepath)

    listen_addr = config.get('general', 'listen_addr')
    listen_addr = listen_addr if listen_addr else ''

    listen_port = config.getint('general', 'listen_port')

    incomming = dict()
    outgoing = dict()

    for sec in config.sections():
        if sec.startswith('inc_'):
            name = config.get(sec, 'name')
            url = config.get(sec, 'url')
            days = config.getfloat(sec, 'update_days')
            incomming[name] = incomming_blacklist(name, url, days)

    for sec in config.sections():
        if sec.startswith('out_'):
            name = config.get(sec, 'name')
            lists = list()
            for i in config.items(sec):
                if i[0].startswith('list_'):
                    lists.append(incomming[i[1]])
            outgoing[name] = outgoing_blacklist(name, lists)

    root = root_resource(outgoing.values(), incomming.values())

    reactor.listenTCP(listen_port, server.Site(root), interface=listen_addr)
    reactor.run()

