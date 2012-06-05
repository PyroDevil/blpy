'''
Created on 09.04.2012

@author: pyro
'''

import os
import time
import signal
from ConfigParser import SafeConfigParser
from pickle import Pickler, Unpickler

from twisted.internet import reactor
from twisted.web import server

from Client import incomming_blacklist
from Server import outgoing_blacklist, root_resource

incomming = dict()
outgoing = dict()
config = None

def shutdown_handler(signum, frame):
    if reactor.running:
        print("Send Reactor stop")
        reactor.callFromThread(reactor.stop)


def StartServer(configfilepath, load_persistent=False, save_persistent=False):
    global incomming, outgoing, config

    config = SafeConfigParser(allow_no_value=True)
    config.read(configfilepath)

    listen_addr = config.get('general', 'listen_addr')
    listen_addr = listen_addr if listen_addr else ''

    listen_port = config.getint('general', 'listen_port')

    persistent_storage = config.get('general', 'persistent_storage')

    #signal.signal(signal.SIGTERM, shutdown_handler)
    #signal.signal(signal.SIGQUIT, shutdown_handler)

    if (load_persistent and
        os.path.exists(persistent_storage) and
        os.path.getmtime(configfilepath) <=
        os.path.getmtime(persistent_storage)):
        with open(persistent_storage, 'rb') as persistent_file:
            (incomming, outgoing) = Unpickler(persistent_file).load()
    else:
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

    if save_persistent :
        with open(persistent_storage, 'wb') as persistent_file:
            Pickler(persistent_file).dump((incomming, outgoing))

