#
# We extract the CoNLLU format for complete sentences
# based on pattern matching of the lines
# This utility converts each input -conllu.text file
# into a -vs-conllu.text file

import sys

SENTENCE_ID_PATTERN = '# sent_id = '
ROOT_PATTERN = '0\troot\t'
VERB_PATTERN = 'VERB'

INFILE_PATTERN = '-conllu.text'
OUTFILE_PATTERN = '-vs-conllu.text'


def flush_current_sentence(current_sentence, stream):
    for line in current_sentence:
        print(line, file=stream)


def add_sentences_with_verbs(filename, stream):
    current_sentence = []
    keep = True
    for connlu_record in (line.rstrip('\n') for line in open(filename)):
        if connlu_record.startswith(SENTENCE_ID_PATTERN):
            if keep and len(current_sentence) > 0:
                flush_current_sentence(current_sentence, stream)
            current_sentence = [connlu_record]
            keep = True
        elif ROOT_PATTERN in connlu_record and not VERB_PATTERN in connlu_record:
            keep = False
        elif keep:
            current_sentence.append(connlu_record)
    # see if anything has lingered
    if keep:
        flush_current_sentence(current_sentence, stream)
    return stream


if __name__ == '__main__':
    outfile = None
    for argument in sys.argv[1:]:
        if argument.endswith('-conllu.text'):
            infile = argument
            outfile = infile[:-len(INFILE_PATTERN)] + OUTFILE_PATTERN
            with open(outfile, 'w') as outfile:
                add_sentences_with_verbs(argument, outfile)
        else:
            raise ValueError(argument)

