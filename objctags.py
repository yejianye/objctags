#!/usr/bin/env python
from argh import dispatch_command, arg
import sys
import re
from string import Template

test_method_regex = re.compile(r'^\s*[+|-]\s*\(.*[^; ]\s*$')
def test_method(line, index, lines):
    return test_method_regex.match(line)

method_prefix_regex = re.compile(r'[+|-]\s*\(.+?\)')
method_sig1_regex = re.compile(r'^(\w+)\s*\{?$')
method_sig2_regex = re.compile(r'\s*(\w+:)')
def parse_method(line):
    line = method_prefix_regex.sub('', line.strip(), 1).strip()
    match_sig1 = method_sig1_regex.match(line)
    if match_sig1:
        return match_sig1.groups()[0]
    else:
        return ''.join(method_sig2_regex.findall(line))
    
tag_kinds = (
    ('m', 'method', test_method, parse_method),
)

def gen_tags(fname, output):
    lines = open(fname).readlines()
    lines = [l.strip('\n') for l in lines]
    results = [process_line(fname, line, idx, lines) for idx, line in enumerate(lines)]
    output.writelines(r + '\n' for r in results if r)

def process_line(fname, line, index, lines, context=None):
    for short_kind, long_kind, test, parse in tag_kinds:
        if test(line, index, lines): 
            tag = parse(line)
            return format_tag(tag, fname, line, index, long_kind)
    return None

# read_rev_sources    schemamaker.py  /^def read_rev_sources(where, rev_tablename, tables):$/;"   function    line:288
tag_tmpl = Template('$tag\t$fname\t/^$line$$/;"\t$long_kind\tline:$lineno')
def format_tag(tag, fname, line, index, long_kind):
    return tag_tmpl.substitute({
        'tag' : tag,
        'fname' : fname,
        'line' : line.rstrip('\n'),
        'lineno' : index+1,
        'long_kind' : long_kind,
    })

@dispatch_command
@arg('FILES', nargs='+', help='objc source files')
def main(args):
    for fname in args.FILES:
        gen_tags(fname, sys.stdout)
