#!/usr/bin/env python
#-*- coding: utf-8 -*-


import fs
import StringIO
import json
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import pdb
import re
import json

try:
    import lxml
    __PARSER__='xml'
except ImportError:
    __PARSER__ = ''


class Scorm(object):
    def __init__(self, scorm_file):
        super(Scorm, self).__init__()
        self.scorm_file = scorm_file
        self.parse()

    def __repr__(self):
        return "Scorm representation for '{0}'".format(self.scorm_file)

    def _et_parse(self, scorm_xml):
        try:
            fileHandler = StringIO.StringIO()
            fileHandler.write(scorm_xml.encode('utf-8'))

            print fileHandler.getvalue()

            tree = ET.parse(fileHandler)
        except IOError:
            pass
        else:
            # pdb.set_trace()
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
                # pdb.set_trace()
                # print list(organization.iter())

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

    def _bs_parse(self, scorm_xml):

        b = BeautifulSoup(scorm_xml, 'xml')
        orgs = dict()
        resources = list(b.resources)
        for org in b.organizations.children:
            print org.string
            # title = org.contents
            # print title
            # for k, v in org.__dict__.items():
            #     if k is not 'parent':
            #         print k, v
            # print org.__dict__
            # print org.attrs
            # print help(org)
            # for e in org:
                # help(e)
            # if 'contents' in org.__dict__.keys():
            #     print org.contents
            # # else:
            #     print org
            # print org.__dict__.keys()
            # print
            # print org.title.contents
            # print org.item
            # print b.resources
            print

        return orgs


    def parse(self):
        try:
            with fs.open_fs('zip://{0}'.format(self.scorm_file)) as zipfs:
                scorm_xml = zipfs.gettext(u'/imsmanifest.xml')
                # orgs = self._et_parse(scorm_xml)
                orgs = self._bs_parse(scorm_xml)

                print json.dumps(orgs, indent=4)
                return orgs

        except fs.errors.ResourceNotFound as e:
            print("Invalid SCORM file")

def main():
    s = Scorm('./la_seguridad_social.zip')
    print(s)



if __name__ == '__main__':
    main()
