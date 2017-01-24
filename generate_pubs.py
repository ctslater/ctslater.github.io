#!/bin/env/python

from __future__ import print_function, division
#
# This should really be run in python 3 to get UTF-8 support right. Otherwise
# non-ASCII names will be messed up.

# This module comes from https://github.com/andycasey/ads
import ads
import yaml
import codecs
from string import Template

entry_template = u"""
<p>{entry_n:d}. <a href="http://adsabs.harvard.edu/abs/{bibcode:s}">{title:s}</a><br>
{authors:s} {year:s}, {journal:s}, {volume:s}, {page:s}.</p>
"""

def parse_journal_abbrev(bibcode):
    """The default search doesn't return the actual journal name, so
    instead I pull it out of the bibcode itself. This is handy since
    I want ApJ not Astrophysical Journal anyways."""
    return bibcode[4:].split('.')[0]

def first_entry(x):
    if type(x) == list:
        return x[0]
    else:
        return x

def format_bibcode(bibcode, entry_n):
    fields = ['title', 'author', 'year', 'issue', 'page']
    search_results = ads.SearchQuery(bibcode=bibcode, fl=fields)
    search_results.execute()

    if(len(search_results.articles) == 0):
        print("Did not obtain any results for bibcode {:s}, skipping".format(bibcode))
        return ""

    paper = search_results.articles[0]

    entry = entry_template.format(entry_n=entry_n,
                                  bibcode=bibcode,
                                  title=first_entry(paper.title),
                                  authors=", ".join(paper.author),
                                  year=paper.year,
                                  journal=parse_journal_abbrev(bibcode),
                                  volume=paper.issue or "",
                                  page=first_entry(paper.page))
    return entry

def format_bibcode_list(bibcode_list):
    out = ""
    inverse_count = range(len(bibcode_list),0, -1)
    for n, bibcode in zip(inverse_count, bibcode_list):
        print(bibcode)
        entry = format_bibcode(bibcode, n)
        out += entry
    return out

if __name__ == "__main__":
    f_bibcodes = open("bibcode_list.yaml")
    paper_bibcodes = yaml.load(f_bibcodes)

    first_author = format_bibcode_list(paper_bibcodes['first_author'][::-1])
    nth_author = format_bibcode_list(paper_bibcodes['nth_author'][::-1])

    template_file = codecs.open("pubs.template", encoding="utf-8")
    template = Template(template_file.read())

    output_file = codecs.open("pubs.html", "w", encoding="utf-8")
    print(template.substitute({"first_author": first_author,
                               "nth_author": nth_author}), file=output_file)
    output_file.close()

