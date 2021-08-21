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


def convert(parse, cf, left='', right=' ', start_of_line='', end_of_line='\n'):
    # we have no xpos tagging information in the Google NLP API
    xpos_tag = '_'
    for offset, token in enumerate(parse['tokens']):
        id = offset + 1
        text = token['text']['content']
        lemma = token['lemma']
        pos_details = token['partOfSpeech']
        pos_tag = pos_details['tag']
        head = token['dependencyEdge']['headTokenIndex']+1
        if head == id: head = 0 # map the root to 0, by convention
        dep_label = token['dependencyEdge']['label'].lower()
        features = extract_part_of_speech_features(pos_details)
        print(start_of_line, end='', file=cf)
        for value in [id, text, lemma, pos_tag, xpos_tag, features, head, dep_label]:
            print(left, end='', file=cf)
            print(value, end=right, file=cf)
        print('', end=end_of_line, file=cf)

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

