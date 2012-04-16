#!/usr/bin/env python2
'''
Created on 16.04.2012

@author: pyro
'''

import sys

from blpy import Application

if __name__ == '__main__':
    Application.StartServer(sys.argv[1])
