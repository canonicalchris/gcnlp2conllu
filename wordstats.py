# compiles word statistics from the ConLL-U Format

import sys
from enum import Enum, auto
from sys import argv

class Format(Enum):
    PLAIN=auto(),
    CSV=auto(),
    COUNT=auto(),
    UNIQUE=auto()


class LineType(Enum):
    SENTENCE = auto(),
    TEXT = auto(),
    TOKEN = auto(),
    UNKNOWN = auto()


def classify(line):
    if line.startswith('# text_'):
        return LineType.TEXT
    elif line.startswith('# sent_id'):
        return LineType.SENTENCE
    elif line[:1].isdigit():
        return LineType.TOKEN
    else:
        return LineType.UNKNOWN


def gather_word_stats(pf, stats = {}):
    word_count = 0
    for line in pf:
        type = classify(line)
        if type == LineType.SENTENCE:
            if word_count > 0:
                stats[word_count] = stats.get(word_count, 0) + 1
            word_count = 0
        elif type == LineType.TOKEN:
            word_count += 1
        elif type == LineType.TEXT:
            continue
        else:
            raise 'Cannot interpret line {}'.format(line)
    # flush the remainder from the buffer
    if word_count > 0:
        stats[word_count] = stats.get(word_count, 0) + 1
    return stats


def gather_unique_words(pf, uniques={}):
    for line in pf:
        type = classify(line)
        if type == LineType.TOKEN:
            items = line.split('\t')
            form = items[1]
            if form[:1].isalpha():
                word = items[2]
                uniques[form.lower()] = word.lower()
    return uniques


def just_stats(stats, cf=sys.stdout):
    s_lens = list(stats.keys())
    s_lens.sort()
    for s_len in s_lens:
        print('{},{}'.format(s_len, stats[s_len]), file=cf)


def just_uniques(uniques, cf=sys.stdout):
    forms = list(uniques.keys())
    forms.sort()
    for form in forms:
        base_word = uniques[form]
        if form != base_word:
            print('{},{}'.format(form, base_word), file=cf)
        else:
            print(form, file=cf)


if __name__ == '__main__':
    format = Format.PLAIN
    outfile = None
    stats = {}
    uniques = {}
    for arg in argv[1:]:
        if arg.endswith('-conllu.text'):
            with open(arg) as pf:
                if format == Format.COUNT:
                    stats = gather_word_stats(pf, stats)
                elif format == Format.UNIQUE:
                    uniques = gather_unique_words(pf, uniques)
                else:
                    raise 'Format {} not supported yet'.format(format)
        elif arg.endswith('.stat'):
            outfile = arg
            format = Format.COUNT
        elif arg.endswith(('-words.text')):
            outfile = arg
            format = Format.UNIQUE
    # now render them
    if outfile is None:
        if format == Format.UNIQUE:
            just_uniques(uniques)
        else:
            just_stats(stats)
    elif format == Format.COUNT:
        with open(outfile, 'w') as cf:
            just_stats(stats, cf)
    elif format == Format.UNIQUE:
        with open(outfile, 'w') as cf:
            just_uniques(uniques, cf)
    else:
        raise RuntimeError('{} not implemented'.format(format))
