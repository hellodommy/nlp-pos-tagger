# python3.8 buildtagger.py <train_file_absolute_path> <model_file_absolute_path>

import os
import math
import sys
import datetime
import json

WORD_COUNTS = 'WORD_COUNTS'
TAG_COUNTS = 'TAG_COUNTS'
CAP_INITIAL_COUNT = 'CAP_INITIAL_COUNT'
HYPH_COUNT = 'HYPH_COUNT'
SUFFIX_COUNT = 'SUFFIX_COUNT'
UNKNOWN_COUNT = 'UNKNOWN_COUNT'
TAG_TAG_COUNTS = 'TAG_TAG_COUNTS' # P(t(i-1), t(i))
WORD_TAG_COUNTS = 'WORD_TAG_COUNTS'
WORD_TAG_PROBS = 'WORD_TAG_PROBS'
TAG_TAG_PROBS = 'TAG_TAG_PROBS'
CAP_INITIAL_PROBS = 'CAP_INITIAL_PROBS'
HYPH_PROBS = 'HYPH_PROBS'
SUFFIX_PROBS = 'SUFFIX_PROBS'
UNKNOWN_PROBS = 'UNKNOWN_PROB' # P(unknown word|t)
START_TAG = '<start>'
END_TAG = '</end>'
UNK = '<UNK>'
TAGS = {
    '``': 0,
    '#': 1,
    '$': 2,
    "''": 3,
    ',': 4,
    '-LRB-': 5,
    '-RRB-': 6,
    '.': 7,
    ':': 8,
    'CC': 9,
    'CD': 10,
    'DT': 11,
    'EX': 12,
    'FW': 13,
    'IN': 14,
    'JJ': 15,
    'JJR': 16,
    'JJS': 17,
    'LS': 18,
    'MD': 19,
    'NN': 20,
    'NNP': 21,
    'NNPS': 22,
    'NNS': 23,
    'PDT': 24,
    'POS': 25,
    'PRP': 26,
    'PRP$': 27,
    'RB': 28,
    'RBR': 29,
    'RBS': 30,
    'RP': 31,
    'SYM': 32,
    'TO': 33,
    'UH': 34,
    'VB': 35,
    'VBD': 36,
    'VBG': 37,
    'VBN': 38,
    'VBP': 39,
    'VBZ': 40,
    'WDT': 41,
    'WP': 42,
    'WP$': 43,
    'WRB': 44,
}
NUM_PENN_TAGS = len(TAGS)
HYPHEN = '-'

data = {}
data[WORD_COUNTS] = {}
data[TAG_COUNTS] = {}
data[TAG_TAG_COUNTS] = {}
data[WORD_TAG_COUNTS] = {}
data[TAG_TAG_COUNTS][START_TAG] = {}
data[TAG_TAG_PROBS] = {}
data[WORD_TAG_PROBS] = {}
data[CAP_INITIAL_COUNT] = {}
data[HYPH_COUNT] = {}
data[SUFFIX_COUNT] = {}
data[UNKNOWN_COUNT] = {}
data[CAP_INITIAL_PROBS] = {}
data[HYPH_PROBS] = {}
data[SUFFIX_PROBS] = {}

SUFFIXES = ["age", "al", "ance", "ence", "dom", "ee", "er", "or", "hood", "ism", "ist", "ity", "ty", "ment", "ness", "ry", "ship", "sion", "tion", "xion", "able", "ible", "al", "en", "ese", "ful", "i", "ic", "ish", "ive", "ian", "less", "ly", "ous", "y", "ate", "en", "ify", "ize", "ise", "ward", "wards", "wise", "s", "ed", "ing"] 

# TODO: write only probabilities to the data file - runtagger does not need counts

def train_model(train_file, model_file):
    # write your code here. You can add functions as well.

    with open(train_file) as rf:
        lines = rf.readlines()
        for line in lines: # collecting counts
            words_with_tags = line.rstrip().split(' ')
            words = [word_with_tag.rsplit('/', 1)[0]
                     for word_with_tag in words_with_tags]
            tags = [word_with_tag.rsplit('/', 1)[1]
                     for word_with_tag in words_with_tags]
            for i in range(len(words_with_tags)):
                # TODO: remove WORD_COUNTS if not needed
                curr_tag = tags[i]
                word = words[i]
                # start collecting counts for unknown words later
                if word.istitle():
                    data[CAP_INITIAL_COUNT][curr_tag] = data[CAP_INITIAL_COUNT].get(curr_tag, 0) + 1
                if HYPHEN in word:
                    data[HYPH_COUNT][curr_tag] = data[HYPH_COUNT].get(curr_tag, 0) + 1
                word = word.lower()
                for suffix in SUFFIXES:
                    if word.endswith(suffix):
                        if suffix in data[SUFFIX_COUNT]:
                            data[SUFFIX_COUNT][suffix][curr_tag] = data[SUFFIX_COUNT][suffix].get(curr_tag, 0) + 1
                        else:
                            data[SUFFIX_COUNT][suffix] = {}
                            data[SUFFIX_COUNT][suffix][curr_tag] = 1
                # end collecting counts for unknown words later
                data[WORD_COUNTS][word] = data[WORD_COUNTS].get(word, 0) + 1
                data[TAG_COUNTS][curr_tag] = data[TAG_COUNTS].get(curr_tag, 0) + 1
                if i == 1: # special case for first word
                    data[TAG_TAG_COUNTS][START_TAG][curr_tag] = data[TAG_TAG_COUNTS][START_TAG].get(curr_tag, 0) + 1
                if word in data[WORD_TAG_COUNTS]:
                    data[WORD_TAG_COUNTS][word][curr_tag] = data[WORD_TAG_COUNTS][word].get(curr_tag, 0) + 1
                else:
                    data[WORD_TAG_COUNTS][word] = {}
                    data[WORD_TAG_COUNTS][word][curr_tag] = 1
                if i != len(words_with_tags) - 1: # if not last word
                    next_tag = tags[i + 1]
                    if curr_tag in data[TAG_TAG_COUNTS]:
                        data[TAG_TAG_COUNTS][curr_tag][next_tag] = data[TAG_TAG_COUNTS][curr_tag].get(next_tag, 0) + 1
                    else:
                        data[TAG_TAG_COUNTS][curr_tag] = {}
                        data[TAG_TAG_COUNTS][curr_tag][next_tag] = 1
                else: # is last word
                    if curr_tag in data[TAG_TAG_COUNTS]:
                        data[TAG_TAG_COUNTS][curr_tag][END_TAG] = data[TAG_TAG_COUNTS][curr_tag].get(END_TAG, 0) + 1
                    else:
                        data[TAG_TAG_COUNTS][curr_tag] = {}
                        data[TAG_TAG_COUNTS][curr_tag][END_TAG] = 1
        # collecting unknown word count (singletons)
        for word in data[WORD_TAG_COUNTS]:
            for tag in data[WORD_TAG_COUNTS][word]:
                if data[WORD_TAG_COUNTS][word][tag] == 1:
                    data[UNKNOWN_COUNT][tag] = data[UNKNOWN_COUNT].get(tag, 0) + 1
        # calculate probabiltiies
        # for P(word|tag)
        for word in data[WORD_TAG_COUNTS]:
            data[WORD_TAG_PROBS][word] = {}
            tags = data[WORD_TAG_COUNTS][word]
            for tag in tags:
                data[WORD_TAG_PROBS][word][tag] = math.log((data[WORD_TAG_COUNTS][word][tag])/(data[TAG_COUNTS][tag]), 10)
        # for P(tag|tag)
        # todo P(unseen tag | seen tag)??
        for first_tag in data[TAG_TAG_COUNTS]:
            data[TAG_TAG_PROBS][first_tag] = {}
            for second_tag in data[TAG_TAG_COUNTS][first_tag]:
                if first_tag == START_TAG:
                    data[TAG_TAG_PROBS][first_tag][second_tag] = math.log((data[TAG_TAG_COUNTS][first_tag][second_tag])/(len(lines)), 10)
                else:
                    data[TAG_TAG_PROBS][first_tag][second_tag] = math.log((data[TAG_TAG_COUNTS][first_tag][second_tag])/(data[TAG_COUNTS][first_tag]), 10)
        # for P(capital|t)
        for tag in data[CAP_INITIAL_COUNT]:
            data[CAP_INITIAL_PROBS][tag] = math.log((data[CAP_INITIAL_COUNT][tag])/(data[TAG_COUNTS][tag]), 10)
        # for P(hyphen|t)
        for tag in data[HYPH_COUNT]:
            data[HYPH_PROBS][tag] = math.log((data[HYPH_COUNT][tag])/(data[TAG_COUNTS][tag]), 10)
        for suffix in data[SUFFIX_COUNT]:
            data[SUFFIX_PROBS][suffix] = {}
            for tag in data[SUFFIX_COUNT][suffix]:
                data[SUFFIX_PROBS][suffix][tag] = math.log((data[SUFFIX_COUNT][suffix][tag])/(data[TAG_COUNTS][tag]), 10)

    with open(model_file, 'w') as wf:
        json_obj = json.dumps(data, indent=2)
        wf.write(json_obj)
    print('Finished...')

if __name__ == "__main__":
    # make no changes here
    train_file = sys.argv[1]
    model_file = sys.argv[2]
    start_time = datetime.datetime.now()
    train_model(train_file, model_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
