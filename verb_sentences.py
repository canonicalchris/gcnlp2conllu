#
# A tool to boil the CoNNL output down to complete sentences,
# i.e. sentences that have at verb root.
# Instead of laborious introspection into the JSON, we effectively run
# (GNU) grep -E '(text_en|0\sroot\s)' FILES-connlu.text
# and then do analysis for cases where VERB lines follow text_en lines
#

import sys
import csv

ENGLISH_TEXT_PATTERN = '# text_en = '
ROOT_PATTERN = '0\troot\t'
VERB_PATTERN = 'VERB'

def add_sentences_with_verbs(filename, sentences):
    current_sentence = None
    for connlu_record in (line.strip() for line in open(filename)):
        if connlu_record.startswith(ENGLISH_TEXT_PATTERN):
            current_sentence = connlu_record[len(ENGLISH_TEXT_PATTERN):]
        elif ROOT_PATTERN in connlu_record and VERB_PATTERN in connlu_record:
            if current_sentence is None:
                raise ValueError
            else:
                sentences.append(current_sentence)
            current_sentence = None
    return sentences


if __name__ == '__main__':
    outfile = None
    sentences = []
    for argument in sys.argv[1:]:
        if argument.endswith('.csv'):
            outfile = argument
        elif argument.endswith('-conllu.text'):
            sentences = add_sentences_with_verbs(argument, sentences)
        else:
            raise ValueError(argument)
    with open(outfile, 'w', newline='') as csv_file:
        cf = csv.writer(csv_file, delimiter=',',
                        quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        for sentence in sentences:
            cf.writerow([sentence])