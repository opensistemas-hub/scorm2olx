#!/usr/bin/env python
#-*- coding: utf-8 -*-


import fs
from fs.tarfs import TarFS
import shutil
import sys
from jinja2 import Template


__COURSE_XML__ = '<course url_name="course" org="{{ org }}" course="{{ course }}"/>'
__COURSE_COURSE_XML__ = """
<course
    advanced_modules="[&quot;videoalpha&quot;, &quot;annotatable&quot;, &quot;scormxblock&quot;, &quot;google-document&quot;]"
    cert_html_view_enabled="true"
    display_name="{{ course_name }}"
    language="en"
    start="&quot;2030-01-01T00:00:00+00:00&quot;">
  <wiki slug="{{org}}.{{course}}.2030"/>
</course>
"""

class OLX(object):
    def __init__(self, olx_file):
        super(OLX, self).__init__()
        self.olx_file = olx_file
        self.skel()

    def skel(self):
        with TarFS('{0}'.format(self.olx_file), write=True) as zipfs:

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

            zipfs.makedirs(u'chapter')
            zipfs.makedirs(u'sequential')
            zipfs.makedirs(u'vertical')

            zipfs.makedirs(u'tabs')
            zipfs.makedirs(u'html')

            zipfs.makedirs(u'course')
            tpl = Template(__COURSE_XML__)

            zipfs.settext(u'course.xml', tpl.render({
                "org": "OS",
                "course": "4"
            }))

            tpl = Template(__COURSE_COURSE_XML__)
            zipfs.settext(u'course/course.xml', tpl.render({
            "org": "OS",
            "course": "4",
            "course_name": self.olx_file
            }))

            print zipfs.listdir(u'/')

    


def main():
    try:
        o = OLX(sys.argv[1])
    except Exception as e:
        print e
        print "No-op"

if __name__ == '__main__':
    main()
