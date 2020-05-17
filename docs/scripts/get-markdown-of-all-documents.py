#!/usr/bin/env python

import argparse
import glob
from collections import defaultdict
from pathlib import Path

# `pip install --user ruamel.yaml`
from ruamel.yaml import YAML
from ruamel.yaml.composer import ComposerError
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError

yaml = YAML(typ='safe')   # default, if not specfied, is 'rt' (round-trip)


def group_by(func, values):
    """ Groups values by func.

    Returns
      (dict): Keys produced by func pointing to lists of the values grouped.
    """
    groups = defaultdict(list)
    for value in values:
        groups[func(value)].append(value)
    return dict(groups)


parser = argparse.ArgumentParser()
parser.add_argument("--startdir", default=".", help="directory to begin")
parser.add_argument("--extension", default=".md", help="extension to grab")
parser.add_argument("--base-url", default="https://faenrandir.github.io/a_careful_examination")
args = parser.parse_args()

files = glob.glob(args.startdir.rstrip("/") + f"/**/*{args.extension}", recursive=True)


def is_valid_header(data):
    return isinstance(data, dict) and ('title' in data) and ('permalink' in data)


def get_header(infile):
    docs = yaml.load_all(Path(infile))
    try:
        header_doc = next(docs)
    except (ScannerError, ComposerError, ParserError):
        return None

    return header_doc if is_valid_header(header_doc) else None


attempted_header = [get_header(infile) for infile in files]
headers = [header for header in attempted_header if header is not None]

grouped = group_by(lambda data: data.get('maintopic', 'unclassified'), headers)

for topic, headers in dict(sorted(grouped.items())).items():
    print(f"### {topic}")
    print()
    for header in headers:
        url = args.base_url + header['permalink']
        title = header['title']
        print(f"* [{title}]({url})")
    print()
