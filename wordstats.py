# compiles word statistics from the ConLL-U Format

import sys
from enum import Enum, auto
from sys import argv

class Format(Enum):
    PLAIN=auto(),
    CSV=auto(),
    COUNT=auto()


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


def just_stats(stats, cf=sys.stdout):
    s_lens = list(stats.keys())
    s_lens.sort()
    for s_len in s_lens:
        print('{},{}'.format(s_len, stats[s_len]), file=cf)


if __name__ == '__main__':
    format = Format.PLAIN
    outfile = None
    stats = {}
    for arg in argv[1:]:
        if arg.endswith('-conllu.text'):
            with open(arg) as pf:
                stats = gather_word_stats(pf, stats)
        elif arg.endswith('.stat'):
            outfile = arg
            format = Format.COUNT
    if outfile is None:
        just_stats(stats, sys.stdout)
    elif format == Format.COUNT:
        with open(outfile, 'w') as cf:
            just_stats(stats, cf)
    else:
        raise RuntimeError('{} not implemented'.format(format))
