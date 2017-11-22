#!/usr/bin/env python
#-*- coding: utf-8 -*-


import fs
import StringIO
import json
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import pdb
import re
import os
import sys
import json
import mimetypes

mimetypes.init()

try:
    import lxml
    __PARSER__='xml'
except ImportError:
    __PARSER__ = ''

def mimeparse(f, zipfs):
    # print
    # print zipfs.getinfo(u'{0}'.format(f)).__dict__
    # print

    return f


class Scorm(object):
    def __init__(self, scorm_file):
        super(Scorm, self).__init__()
        self.scorm_file = scorm_file

    def __repr__(self):
        return "Scorm representation for '{0}':\n\n{1}".format(
                self.scorm_file,
                json.dumps(self.parse(), indent=4)
            )


    """
        Legacy Code from old parser
    """
    def _et_parse(self, scorm_xml):
        try:
            fileHandler = StringIO.StringIO()
            fileHandler.write(scorm_xml.encode('utf-8'))

            print fileHandler.getvalue()

            tree = ET.parse(fileHandler)
        except IOError:
            pass
        else:
            namespace = ''
            nodes = [node for _, node in ET.iterparse(fileHandler, events=['start-ns'])]

            for node in nodes:
                if node[0] == '':
                    namespace = node[1]
                    break
            root = tree.getroot()


            if namespace:
                resources = root.find('{{{0}}}resources'.format(namespace))
                schemaversion = root.find('{{{0}}}metadata/{{{0}}}schemaversion'.format(namespace))
                organizations = root.find('{{{0}}}organizations'.format(namespace))
            else:
                resources = root.find('resources')
                schemaversion = root.find('metadata/schemaversion')
                organizations = root.find('organizations')

            orgs = list()
            for organization in organizations:

                org = dict()
                texts = filter(lambda x: x if not re.match('\s', x) else None,
                        map(lambda x: x.text, organization.iter())
                    )
                # print "Texts", texts
                if len(texts):
                    title = texts[0]

                with_identifier = filter(lambda x: 'identifierref' in x.keys(),
                        map(
                            lambda x: x,
                            filter(lambda x: len(x.items()) > 0, organization.iter())
                        )
                    )

                # print val
                if len(with_identifier):
                    val = with_identifier[0]
                    identifier = val.get('identifier')
                    identifierref = val.get('identifierref')

                org.update({
                    "title": title,
                    "identifier": identifier,
                    "identifierref": identifierref
                })

                if resources is not None:
                    resource = filter(lambda x: x.get('identifier')==identifierref, resources)
                    if resource:
                        resource = resource[0]
                        path_index_page = resource.get('href')
                        # print resource.items()
                        identifier = resource.get('identifier')
                        files = map(lambda x: x.get('href'), resource)
                        org.update({'index': path_index_page})
                        org.update({'files': sorted(files)})
                orgs.append(org)

                return org

    def _bs_parse(self, scorm_xml, zipfs):

        b = BeautifulSoup(scorm_xml, 'xml')
        data = {
            "zipfile": self.scorm_file,
            "orgs": list()
        }
        for org in b.organizations.find_all('item'):
            d_org = dict()
            d_org.update({
            'title': org.title.text,
            'identifier': org.get('identifier'),
            'identifierref': org.get('identifierref')
            })

            resource = list(b.find_all('resource', identifier=org.get('identifierref')))[0]
            files = map(lambda x: mimeparse(x.get('href'), zipfs), resource.find_all('file'))
            index_href = resource.get('href', 'index.html')
            dirname = os.path.dirname(index_href)
            index_html = zipfs.gettext(u'/{0}'.format(index_href))

            # Parse index_html to find out whether a popup exists
            m = re.search(r"window\.open\(\"(?P<url>[\w+\/\.]+)\",", index_html)
            if m:
                index_href = os.path.join(dirname, m.group('url'))

            d_org.update({
                "index": index_href,
                "files": sorted(files)
            })
            data['orgs'].append(d_org)
        return data





    def parse(self):
        try:
            with fs.open_fs('zip://{0}'.format(self.scorm_file)) as zipfs:
                scorm_xml = zipfs.gettext(u'/imsmanifest.xml')
                orgs = self._bs_parse(scorm_xml, zipfs=zipfs)
                return orgs
        except fs.errors.ResourceNotFound as e:
            print("Invalid SCORM file")
            print(e)

def main():
    print sys.argv[1]
    s = Scorm(sys.argv[1])
    print(s)



if __name__ == '__main__':
    main()
