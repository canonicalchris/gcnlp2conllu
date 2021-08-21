# Does a Google Cloud NLP JSON to CoNLL-U Transformation
# @see https://universaldependencies.org/format.html
#
import sys
from sys import argv
import json


def convert_to_html(parse, cf):
    convert(parse, cf, left='<td>', right='</td>')


def convert(parse, cf, left='', right=' '):
    for offset, token in enumerate(parse['tokens']):
        id = offset + 1
        text = token['text']['content']
        lemma = token['lemma']
        pos_tag = token['partOfSpeech']['tag']
        head = token['dependencyEdge']['headTokenIndex']+1
        if head == id: head = 0 # map the root to 0, by convention
        dep_label = token['dependencyEdge']['label'].lower()
        # we have no XPOS information, i.e. english-specific POS information
        for value in [id, text, lemma, pos_tag, head, dep_label]:
            print(left, end='', file=cf)
            print(value, end=right, file=cf)
        print('', file=cf)


if __name__ == '__main__':
    with open(argv[1]) as pf:
        parse = json.load(pf)
    if len(argv) < 3:
        convert(parse, sys.stdout)
    else:
        with open(argv[2], 'w') as cf:
            convert(parse, cf)

