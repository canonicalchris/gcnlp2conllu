# Does a Google Cloud NLP JSON to CoNLL-U Transformation
# @see https://universaldependencies.org/format.html
#
import sys
from io import StringIO
from sys import argv
import json



def extract_part_of_speech_features(pos_details):
    features = StringIO()
    first = True
    for key, value in pos_details.items():
        if key == 'tag' or value.endswith("_UNKNOWN"):
            continue
        if first:
            first = False
        else:
            features.write('|')
        features.write(key.capitalize())
        features.write('=')
        features.write(value.capitalize())
    return features.getvalue()


def convert_to_html(parse, cf):
    print("<table><tbody>", file=cf)
    convert(parse, cf, start_of_line='<tr>', left='<td>', right='</td>', end_of_line='</tr>\n')
    print("</tbody></table>", file=cf)
    print('', file=cf)


def write_conllu_record(values, start_of_line, left, right, end_of_line, cf):
    print(start_of_line, end='', file=cf)
    for value in values:
        print(left, end='', file=cf)
        print(value, end=right, file=cf)
    print('', end=end_of_line, file=cf)


# note that we do not actually need to compile a sentence index, since the list is
# ordered in ascending order and we can do a straight-up merge ... rck 20210906
def compile_sentence_index(sentences):
    index = {}
    for sentence in sentences:
        details = sentence['text']
        offset = details['beginOffset']
        text = details['content']
        index[offset] = text
    return index


# Because we need to know how far the next token is to compute the SpaceAfter=No property
# correctly, we use a buffer of depth one to edit the meta-properties for Token K when
# looking at the token of K+1
# We also number the sentences and renumber the nodes relative to the sentence
def convert(parse, cf, left='', right='\t', start_of_line='', end_of_line='\n', meta_info=True):
    # we have no xpos tagging information in the Google NLP API
    sentence_index = compile_sentence_index(parse['sentences'])
    sentence_id = 0
    sentence_base_token_id = 0
    id = 1
    prev_tail = -1
    values = []
    for item_number, token in enumerate(parse['tokens']):
        offset = token['text']['beginOffset']
        text = token['text']['content']
        # if this becomes a bottleneck, consider
        # @see https://stackoverflow.com/questions/6714826/how-can-i-determine-the-byte-length-of-a-utf-8-encoded-string-in-python
        curr_tail = offset + len(text.encode('utf-8'))
        if offset == prev_tail:
            values[-1] = 'SpaceAfter=No'
        if len(values) > 0:
            write_conllu_record(values, start_of_line, left, right, end_of_line, cf)
        if meta_info and offset in sentence_index:
            id = 1
            sentence_base_token_id = item_number
            sentence_id += 1
            print(start_of_line, end='', file=cf)
            print('# sent_id = {}'.format(sentence_id), end=end_of_line, file=cf)
            print(start_of_line, end='', file=cf)
            print('# text_en = {}'.format(sentence_index[offset]), end=end_of_line, file=cf)
        lemma = token['lemma']
        pos_details = token['partOfSpeech']
        pos_tag = pos_details['tag']
        head = token['dependencyEdge']['headTokenIndex']
        if head == item_number:
            head = 0 # map the root to 0, by convention
        else:
            head = head - sentence_base_token_id + 1 # make it relative to the sentence at hand
        dep_label = token['dependencyEdge']['label'].lower()
        features = extract_part_of_speech_features(pos_details)
        xpos_tag = pos_tag
        values = [id, text, lemma, pos_tag, xpos_tag, features, head, dep_label, '_', '_']
        id += 1
        prev_tail = curr_tail
    # flush any remainder in the buffer
    if len(values) > 0:
        write_conllu_record(values, start_of_line, left, right, end_of_line, cf)


if __name__ == '__main__':
    with open(argv[1]) as pf:
        parse = json.load(pf)
    if len(argv) < 3:
        convert(parse, sys.stdout)
    else:
        outfile = argv[2]
        with open(outfile, 'w') as cf:
            if outfile.endswith('.html'):
                convert_to_html(parse, cf)
            else:
                convert(parse, cf)

