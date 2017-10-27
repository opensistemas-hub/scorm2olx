#!/usr/bin/env python
#-*- coding: utf-8 -*-


import fs
import shutil
import sys

class OLX(object):
    def __init__(self, olx_file):
        super(OLX, self).__init__()
        self.olx_file = olx_file
        self.skel()

    def skel(self):
        with fs.open_fs('zip://{0}'.format(self.olx_file), writeable=True, create=True) as zipfs:

            zipfs.makedirs(u'about')
            zipfs.touch(u'/about/overview.html')
            zipfs.touch(u'/about/short_description.html')


            zipfs.makedirs(u'info')
            zipfs.touch(u'/info/updates.html')
            zipfs.touch(u'/info/handouts.html')

            zipfs.makedirs(u'policies')
            zipfs.touch(u'/policies/grading_policy.json')
            zipfs.touch(u'/policies/policy.json')
            zipfs.touch(u'/policies/assets.json')

            zipfs.makedirs(u'problem')
            zipfs.makedirs(u'static')
            zipfs.makedirs(u'vertical')
            zipfs.makedirs(u'tabs')
            zipfs.makedirs(u'html')

            zipfs.touch(u'course.xml')

            print zipfs.listdir(u'/')


def main():
    try:
        o = OLX(sys.argv[1])
    except Exception as e:
        print e
        print "No-op"

if __name__ == '__main__':
    main()
