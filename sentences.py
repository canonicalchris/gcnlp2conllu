# Does a Google Cloud NLP JSON to CoNLL-U Transformation
# @see https://universaldependencies.org/format.html
#
import sys
from enum import Enum, auto
from sys import argv
import json
import csv


class Format(Enum):
    PLAIN=auto(),
    CSV=auto


def collate_sentences(json_parse, file_id, seen = {}):
    for sentence in (json_parse['sentences']):
        text = sentence['text']['content']
        file_ids = seen.get(text, [])
        if file_id not in file_ids:
            file_ids.append(file_id)
            seen[text] = file_ids
    return seen


def extract_sentences(seen):
    at_least_once = seen.keys()
    multiple = []
    for sentence in at_least_once:
        count = len(seen[sentence])
        while count > 1:
            multiple.append(sentence)
            count -= 1
    all = list(at_least_once) + multiple
    all.sort()
    return all


def just_sentences(sentences, cf=sys.stdout, format=Format.PLAIN):
    for sentence in sentences:
        if format == Format.PLAIN:
            print(sentence, file=cf)
        elif format == Format.CSV:
            cf.writerow([sentence])
        else:
            raise RuntimeError('{} not implemented'.format(format))


if __name__ == '__main__':
    format = Format.PLAIN
    outfile = None
    seen = {}
    file_id = 1
    for arg in argv[1:]:
        if arg.endswith('.json'):
            with open(arg) as pf:
                seen = collate_sentences(json.load(pf), file_id, seen)
                file_id += 1
        elif arg.endswith('.text') or arg.endswith('.txt'):
            outfile = arg
        elif arg.endswith('.csv'):
            outfile = arg
            format = Format.CSV
    # we have now loaded all JSON and determine the output target and format
    sentences = extract_sentences(seen)
    if outfile is None:
        just_sentences(sentences, sys.stdout, format)
    elif format == Format.CSV:
        with open(outfile, 'w', newline='') as csvfile:
            cf = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            just_sentences(sentences, cf, Format.CSV)
    else:
        with open(outfile, 'w') as cf:
            just_sentences(sentences, cf, Format.PLAIN)

