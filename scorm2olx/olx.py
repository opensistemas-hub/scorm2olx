#!/usr/bin/env python
#-*- coding: utf-8 -*-


import fs
import os
from mimetypes import MimeTypes
import urllib

try:
    from fs.tarfs import TarFS
except ImportError as e:

    import tarfile
    import tempfile
    import shutil
    import os

    class TarFS(object):

        def __init__(self, tarname, write=True):
            super(TarFS, self).__init__()
            self.tarname = tarname
            self.write = write


        def __enter__(self):
            self.__dirname__ = tempfile.mkdtemp()
            return self

            # mode = 'r:gz'
            # if self.write:
            #     mode = 'w:gz'
            # self.tarfile = tarfile.open(self.tarname, mode=mode)
            # return self.tarfile

        def __exit__(self):
            self.tarfile.open(self.__dirname__, mode='w:gz')
            self.tarfile.close()
            shutil.rmtree(self.__dirname__)

        def makedirs(self, dir):
            os.makedirs(os.path.join(self.__dirname__, dir))

        def settext(self, filename, content=None):
            with open(os.path.join(self.__dirname__, filename), 'w') as f:
                if content:
                    f.write(content)

        def touch(self, filename):
            return self.settext(filename)


    # from tarfs import TarFS
    

try:
    from fs.errors import ResourceNotFound
except ImportError:
    ResourceNotFound = Exception

from fs.osfs import OSFS
try:
    from fs.copy import copy_file
except ImportError:
    def copy_file(from_dir, from_file, to_dir, to_file):
        print from_dir, from_file, to_dir, to_file

import shutil
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
    display_name="{{ course_name }}"
    language="en"
    start="&quot;2030-01-01T00:00:00+00:00&quot;">
    {{ chapters }}
  <wiki slug="{{org}}.{{course}}.2030"/>
</course>
"""

class OLX(object):
    def __init__(self, olx_file):
        super(OLX, self).__init__()
        self.olx_file = olx_file
        # self.tree = dict()
        # self.skel()

    def skel(self):
        with TarFS('{0}'.format(self.olx_file), write=True) as zipfs:

            zipfs.makedirs(u'/about')
            zipfs.touch(u'/about/overview.html')
            zipfs.touch(u'/about/short_description.html')


            zipfs.makedirs(u'/info')
            zipfs.touch(u'/info/updates.html')
            zipfs.touch(u'/info/handouts.html')

            zipfs.makedirs(u'/policies/course')
            zipfs.settext(u'/policies/course/grading_policy.json', u'{}')

            policy = u"""
{
    "course/course": {
        "advanced_modules": [
            "videoalpha",
            "annotatable",
            "scormxblock",
            "google-document"
        ],
        "cert_html_view_enabled": true,
        "discussion_topics": {
            "General": {
                "id": "course"
            }
        },
        "display_name": "SegSocial.zip",
        "language": "en",
        "start": "2030-01-01T00:00:00Z",
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
}"""

            try:
                pol = json.loads(policy)
            except Exception as e:
                print (e)
                sys.exit(3)

            zipfs.settext(u'/policies/course/policy.json', u'{0}'.format(json.dumps(pol)))


            zipfs.makedirs(u'/problem')
            zipfs.makedirs(u'/static')

            zipfs.makedirs(u'/chapter')
            zipfs.makedirs(u'/sequential')
            zipfs.makedirs(u'/vertical')

            zipfs.makedirs(u'/tabs')
            zipfs.makedirs(u'/html')

            zipfs.makedirs(u'course')
            tpl = Template(__COURSE_XML__)

            # zipfs.settext(u'course.xml', tpl.render({
            #     "org": "OS",
            #     "course": "4"
            # }))
            zipfs.settext(u'course.xml', tpl.render({
            "org": "OS",
            "course": "4"
            }))


            tpl = Template(__COURSE_COURSE_XML__)
            zipfs.settext(u'course/course.xml', tpl.render({
            "org": "OS",
            "course": "4",
            "course_name": self.olx_file,
            "chapters": self.add_chapters(zipfs)
            }))


    def add_tree(self, tree):
        self.tree = tree

    def add_chapters(self, zipfs):
        chapters = ""
        for chapter in self.tree['orgs']:
            chapters += '\n' + self.add_chapter(chapter, zipfs)
        zipfs.settext(u'/policies/assets.json', self.fHandler(zipfs))
        return chapters

    def fHandler(self, zipfs):
        zipfile = self.tree['zipfile']
        assets = {}
        if zipfile:
            try:
                with fs.open_fs('zip://{0}'.format(zipfile)) as scorm_zipfs:
                    copy_file(
                        unicode(os.path.dirname(zipfile)),
                        unicode(os.path.basename(zipfile)),
                        zipfs,
                        u'/static/{}'.format(os.path.basename(zipfile))
                    )
                    # Walk
                    mime = MimeTypes()
                    for asset in filter(lambda a: re.match(r'^\/static', a), zipfs.walk.files()):
                        contentType = mime.guess_type(asset)[0]
                        _asset = os.path.basename(asset)
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
                                    "import_path": asset
                            }
                            assets[_asset] = a
            except ResourceNotFound as e:
                print("Invalid SCORM file")
                print(e)
                print "ERROR"

        # print json.dumps(assets, indent=4)
        return unicode(json.dumps(assets))

    def add_chapter(self, chapter, zipfs):
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
        zipfs.settext(u'/chapter/{0}.xml'.format(hash_name), xml_full_chapter)

        xml_full_sequential = Template("""
            <sequential display_name="{{display_name}}">
                <vertical url_name="{{hash_vert}}" />
            </sequential>
        """).render(display_name=title, hash_vert=hash_vert)
        zipfs.settext(u'/sequential/{0}.xml'.format(hash_seq), xml_full_sequential)

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
        zipfs.settext(u'/vertical/{0}.xml'.format(hash_vert), xml_full_vertical)

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
