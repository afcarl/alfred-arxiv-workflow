# -*- coding: utf-8 -*-

# arXiv
# Copyright (c) 2016 Jongwook Choi (@wookayin)

"""
Usage:
    arxiv.py <search_query>
"""

from __future__ import print_function
import sys
import workflow
import arxiv
import urllib
import re

RE_ARXIV = 'https?://arxiv.org/(abs|pdf)/(.*?)(v\d+)?(.pdf)?\)?$'

def parse_arxiv_url(text):
    m = re.match(RE_ARXIV, text)
    _, identifier, v, _ = m.groups()
    return identifier, v


def main(wf):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', default=None, type=str)
    args = parser.parse_args()
    log.debug('args : {}'.format(args))

    query = args.query
    # FUCK arxiv.py is too stupid why it is not quoting
    ret = arxiv.query(urllib.quote(query),
                      max_results=25)

    if not ret:
        wf.add_item('No matchings', icon=workflow.ICON_WARNING)

    for entry in ret:
        title = entry['title']
        authors = ', '.join(entry['authors'])
        bundle = ', '.join(t['term'] for t in entry['tags'])
        url = entry['id']

        identifier, version = parse_arxiv_url(url)     # 1704.12345
        canonical_url = 'https://arxiv.org/abs/%s' % identifier

        item = wf.add_item(
            title="[%s] %s" % (identifier, title),
            subtitle="%s [%s]" % (authors, bundle),
            valid=True,
            arg=identifier,
            uid=identifier,
            type='file',
            #icon='icon.png',
        )
        item.add_modifier('alt', 'http://arxiv.org/pdf/%s' % identifier,
                          arg=identifier)
        item.add_modifier('shift', 'Copy the identifier %s' % identifier,
                          arg=identifier)
        item.add_modifier('cmd', 'Copy the arXiv abs URL: %s' % canonical_url,
                          arg=canonical_url)
        item.add_modifier('ctrl', 'Copy markdown link: [[%s] %s](%s)' % (identifier, title, canonical_url),
                          arg="[[%s] %s](%s)" % (identifier, title, canonical_url))

    wf.send_feedback()
    return 0


if __name__ == '__main__':
    wf = workflow.Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
