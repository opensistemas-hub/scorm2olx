#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import argparse

from scorm import Scorm
from olx import OLX

def from_scorm_to_olx(sc, ol, display_name, org, course, run):
    ol.add_tree(sc.parse())
    ol.skel(display_name, org, course, run)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Input SCORM FILE", required=True)
    parser.add_argument("--display_name", help="Display Name for the Course", required=True)
    parser.add_argument("--org", help="Organization", required=True)
    parser.add_argument("--course", help="Course identifier", required=True)
    parser.add_argument("--run", help="Running identifier. e.g: 1T_2018", required=True)
    parser.add_argument("--output", help="Output Open Learning XML (OLX)", required=True)
    args = parser.parse_args()

    s = Scorm(args.input)
    o = OLX(args.output)

    try:
        from_scorm_to_olx(s, o, args.display_name, args.org, args.course, args.run)
    except Exception:
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)


if __name__ == '__main__':
    main()
