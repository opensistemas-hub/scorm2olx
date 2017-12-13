#!/usr/bin/env python
#-*- coding: utf-8 -*-
from distutils.core import setup

setup(name='scorm2olx',
      author='Javier Muñoz Díaz',
      author_email='jmdiaz@opensistemas.com',
      description='SCORM to Open Learning XML converter',
      version=u'0.0.1',
      packages=['scorm2olx'],
      install_requires=[
            'appdirs==1.4.3',
            'beautifulsoup4==4.6.0',
            'enum34==1.1.6',
            'fs==2.0.12',
            'lxml==4.1.0',
            'pytz==2017.2',
            'scandir==1.6',
            'six==1.11.0',
            'jinja2'
      ],
      url=''
)
