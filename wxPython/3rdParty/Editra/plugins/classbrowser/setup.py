# -*- coding: utf-8 -*-
# Setup script to build the ClassBrowser plugin. To build the plugin
# just run 'python setup.py bdist_egg' and an egg will be built and put into 
# a directory called dist in the same directory as this script.
""" Editra ClassBrowser Plugin """

__author__ = "Cody Precord"

import sys
try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

if setup != None:
    setup(
        name='ClassBrowser',
        version='0.1',
        description=__doc__,
        author=__author__,
        author_email="cprecord@editra.org",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['classbrowser'],
        package_data={'classbrowser' : ['gentag/*.py']},
        entry_points='''
        [Editra.plugins]
        ClassBrowser = classbrowser:ClassBrowser
        '''
        )
