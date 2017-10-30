#!/usr/bin/env python
#-*- coding: utf-8 -*-


import fs
from fs.tarfs import TarFS
from fs.appfs import UserDataFS
import shutil
import sys
from jinja2 import Template
import hashlib

def md5(x):
    import hashlib
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
        self.tree = dict()
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
            zipfs.settext(u'/policies/policy.json',
            u"""
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
                "id": "i4x-OS-4-course-course"
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
        ],
        "xml_attributes": {
            "filename": [
                "course/course.xml",
                "course/course.xml"
            ]
        }
    }
            """)

            zipfs.settext(u'/policies/assets.json', u'{}')

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
            "course_name": self.olx_file,
            "chapters": self.add_chapters(zipfs)
            }))


    def add_tree(self, tree):
        self.tree = tree


    def add_chapters(self, zipfs):
        chapters = ""
        for chapter in self.tree:
            chapters += '\n' + self.add_chapter(chapter, zipfs)
        return chapters

    def add_chapter(self, chapter, zipfs):
        title = chapter.get('title')
        hash_name = md5(title)
        hash_seq = md5(chapter.get('identifier'))
        hash_vert = md5(chapter.get('identifierref'))

        xml_chapter = Template('<chapter url_name="{{url_name}}.xml" />').render(url_name=hash_name)

        xml_full_chapter = Template("""
            <chapter display_name="{{display_name}}">
                <sequential url_name="{{hash_seq}}.xml" />
            </chapter>
        """).render(display_name=title, hash_seq=hash_seq)

        zipfs.settext(u'chapter/{0}.xml'.format(hash_name), xml_full_chapter)
        xml_full_sequential = Template("""
            <sequential display_name="{{display_name}}">
                <vertical url_name="{{hash_vert}}.xml" />
            </sequential>
        """).render(display_name=title, hash_vert=hash_vert)
        zipfs.settext(u'sequential/{0}.xml'.format(hash_seq), xml_full_sequential)

        xml_full_vertical = Template("""
            <vertical display_name="{{display_name}}">
                <scormxblock
                    url_name="{{hash_unit}}"
                    xblock-family="xblock.v1"
                    icon_class="video"
                    has_score="false"
                    display_name="SCORM"
                    scorm_file="{{scorm_file}}"
                    />
            </vertical>
        """).render(
            display_name=title,
            hash_unit=hash_seq,
            scorm_file=chapter.get('index'))
        zipfs.settext(u'vertical/{0}.xml'.format(hash_vert), xml_full_vertical)

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
