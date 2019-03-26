#!/usr/bin/python

import urllib2
value = urllib2.urlopen("http://magyarpeter.com/df").read()
print (value)
