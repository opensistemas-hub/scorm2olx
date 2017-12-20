#!/usr/bin/env python
#-*- coding: utf-8 -*-


import fs
import os
from mimetypes import MimeTypes
import urllib

from fs.zipfs import ZipFS
from tarfs import TarFS

try:
    from fs.errors import ResourceNotFound
except ImportError:
    ResourceNotFound = Exception

import re
import sys
from jinja2 import Template
import hashlib
import json

def md5(x):
    m = hashlib.md5()
    m.update(x.encode('utf-8'))
    return m.hexdigest()

__COURSE_XML__ = '<course url_name="course" org="{{ org }}" course="{{ course }}"/>'
__COURSE_COURSE_XML__ = """
<course
    advanced_modules="[&quot;videoalpha&quot;, &quot;annotatable&quot;, &quot;scormxblock&quot;, &quot;google-document&quot;]"
    cert_html_view_enabled="true"
    display_name="{{ display_name }}"
    language="en"
    start="&quot;9999-01-01T00:00:00+00:00&quot;">
    {{ chapters }}
  <wiki slug="{{org}}.{{course}}.{{run}}"/>
</course>
"""

class OLX(object):
    def __init__(self, olx_file):
        super(OLX, self).__init__()
        self.olx_file = olx_file

    def skel(self, display_name, org, course, run):
        with TarFS('{0}'.format(self.olx_file), write=True) as tarfs:

            tarfs.makedirs(u'/about')
            tarfs.touch(u'/about/overview.html')
            tarfs.touch(u'/about/short_description.html')


            tarfs.makedirs(u'/info')
            tarfs.touch(u'/info/updates.html')
            tarfs.touch(u'/info/handouts.html')

            tarfs.makedirs(u'/policies/course')
            tarfs.settext(u'/policies/course/grading_policy.json', u'{}')

            policy = u"""
{
    "course/course": {
        "advanced_modules": [
            "scormxblock"
        ],
        "cert_html_view_enabled": true,
        "discussion_topics": {
            "General": {
                "id": "course"
            }
        },
        "display_name": "%s",
        "language": "en",
        "start": "9999-01-01T00:00:00Z",
        "tabs": [
            {
                "course_staff_only": false,
                "name": "Home",
                "type": "course_info"
            },
            {
                "course_staff_only": false,
                "name": "Course",
                "type": "courseware"
            },
            {
                "course_staff_only": false,
                "name": "Textbooks",
                "type": "textbooks"
            },
            {
                "course_staff_only": false,
                "name": "Discussion",
                "type": "discussion"
            },
            {
                "course_staff_only": false,
                "name": "Wiki",
                "type": "wiki"
            },
            {
                "course_staff_only": false,
                "name": "Progress",
                "type": "progress"
            }
        ]
    }
}""" % display_name

            try:
                pol = json.loads(policy)
            except Exception as e:
                print (e)
                sys.exit(3)

            tarfs.settext(u'/policies/course/policy.json', u'{0}'.format(json.dumps(pol)))


            tarfs.makedirs(u'/problem')
            tarfs.makedirs(u'/static')

            tarfs.makedirs(u'/chapter')
            tarfs.makedirs(u'/sequential')
            tarfs.makedirs(u'/vertical')

            tarfs.makedirs(u'/tabs')
            tarfs.makedirs(u'/html')

            tarfs.makedirs(u'course')

            tarfs.settext(u'course.xml', Template(__COURSE_XML__).render({
            "org": org,
            "course": course
            }))

            tarfs.settext(u'course/course.xml', Template(__COURSE_COURSE_XML__).render({
            "org": org,
            "course": course,
            "course_name": display_name,
            "chapters": self.add_chapters(tarfs)
            }))


    def add_tree(self, tree):
        self.tree = tree

    def add_chapters(self, tarfs):
        chapters = ""
        for chapter in self.tree['orgs']:
            ch = self.add_chapter(chapter, tarfs)
            if ch:
                chapters += '\n' + ch
        tarfs.settext(u'/policies/assets.json', self.fHandler(tarfs))
        return chapters

    def fHandler(self, tarfs):
        zipfile = self.tree['zipfile']
        assets = {}
        if zipfile:
            try:
                with ZipFS('{0}'.format(zipfile)) as scorm_zipfs:
                    # Add original SCORM file into static content
                    tarfs.copy(zipfile, tarfs.safe_join('/static/', os.path.basename(zipfile)))
                    
                    # Walk
                    mime = MimeTypes()
                    contentType = mime.guess_type(tarfs.safe_join('/static/', zipfile))[0]
                    _asset = os.path.basename(zipfile)

                    if contentType:
                        a = {
                            "contentType": contentType,
                            "displayname": _asset,
                            "locked": "true",
                            "content_son": {
                                "category": "asset",
                                "name": _asset
                                },
                                "filename": u'asset-v1:edx+edx+edx+type@asset+block@{}'.format(_asset),
                                "import_path": zipfile
                        }
                        assets[_asset] = a

            except ResourceNotFound as e:
                print("Invalid SCORM file")
                import traceback
                traceback.print_exc()
                print "ERROR"

        # print json.dumps(assets, indent=4)
        return unicode(json.dumps(assets))

    def add_chapter(self, chapter, tarfs):
        title = chapter.get('title')
        hash_name = md5(title)
        hash_seq = md5(chapter.get('identifier'))
        hash_vert = md5(chapter.get('identifierref'))

        xml_chapter = Template('<chapter url_name="{{url_name}}" />').render(url_name=hash_name)

        xml_full_chapter = Template("""
            <chapter display_name="{{display_name}}">
                <sequential url_name="{{hash_seq}}" />
            </chapter>
        """).render(display_name=title, hash_seq=hash_seq)
        tarfs.settext(u'/chapter/{0}.xml'.format(hash_name), xml_full_chapter)

        xml_full_sequential = Template("""
            <sequential display_name="{{display_name}}">
                <vertical url_name="{{hash_vert}}" />
            </sequential>
        """).render(display_name=title, hash_vert=hash_vert)
        tarfs.settext(u'/sequential/{0}.xml'.format(hash_seq), xml_full_sequential)

        xml_full_vertical = Template("""
            <vertical display_name="{{display_name}}">
                <scormxblock
                    url_name="{{hash_unit}}"
                    xblock-family="xblock.v1"
                    icon_class="video"
                    has_score="false"
                    display_name="{{display_name}}"
                    scorm_file="{{scorm_file}}"
                    scorm_zip_file="{{scorm_zip_file}}"
                    />
            </vertical>
        """).render(
            display_name=title,
            hash_unit=hash_seq,
            scorm_file=chapter.get('index'),
            scorm_zip_file=os.path.basename(self.tree.get('zipfile')))
        tarfs.settext(u'/vertical/{0}.xml'.format(hash_vert), xml_full_vertical)

        return xml_chapter

    def add_sequential(self, display_name, chapter):
        pass

    def add_vertical(self, display_name, sequential):
        pass


def main():
    try:
        o = OLX(sys.argv[1])
    except Exception as e:
        print e
        print "No-op"

if __name__ == '__main__':
    main()
