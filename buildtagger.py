# python3.8 buildtagger.py <train_file_absolute_path> <model_file_absolute_path>

import os
import math
import sys
import datetime
import json

WORD_COUNTS = 'WORD_COUNTS'
TAG_COUNTS = 'TAG_COUNTS'
TAG_BICOUNTS = 'TAG_BICOUNTS' # P(t(i-1), t(i))
WORD_TAG_COUNTS = 'WORD_TAG_COUNTS'
WORD_TAG_PROBS = 'WORD_TAG_PROBS'
TAG_BICOUNT_PROBS = 'TAG_BICOUNT_PROBS'
START_TAG = '<s>'
END_TAG = '</s>'
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

data = {}
data[WORD_COUNTS] = {}
data[TAG_COUNTS] = {}
data[TAG_BICOUNTS] = {}
data[WORD_TAG_COUNTS] = {}
data[TAG_BICOUNTS][START_TAG] = {}
data[TAG_BICOUNTS][END_TAG] = {}
data[TAG_BICOUNT_PROBS] = {}
data[WORD_TAG_PROBS] = {}

def train_model(train_file, model_file):
    # write your code here. You can add functions as well.

    with open(train_file) as rf:
        lines = rf.readlines()
        for line in lines: # collecting counts
            words_with_tags = line.rstrip().split(' ')
            words = [word_with_tag.rsplit('/', 1)[0].lower()
                     for word_with_tag in words_with_tags]
            tags = [word_with_tag.rsplit('/', 1)[1]
                     for word_with_tag in words_with_tags]
            for i in range(len(words_with_tags)):
                data[WORD_COUNTS][words[i]] = data[WORD_COUNTS].get(words[i], 0) + 1
                data[TAG_COUNTS][tags[i]] = data[TAG_COUNTS].get(tags[i], 0) + 1
                if i == 1:
                    data[TAG_BICOUNTS][START_TAG][tags[i]] = data[TAG_BICOUNTS][START_TAG].get(tags[i], 0) + 1
                if words[i] in data[WORD_TAG_COUNTS]:
                    data[WORD_TAG_COUNTS][words[i]][tags[i]] = data[WORD_TAG_COUNTS][words[i]].get(tags[i], 0) + 1
                else:
                    data[WORD_TAG_COUNTS][words[i]] = {}
                    data[WORD_TAG_COUNTS][words[i]][tags[i]] = 1
                if i != len(words_with_tags) - 1: # if not last word
                    if tags[i] in data[TAG_BICOUNTS]:
                        data[TAG_BICOUNTS][tags[i]][tags[i + 1]] = data[TAG_BICOUNTS][tags[i]].get(tags[i + 1], 0) + 1
                    else:
                        data[TAG_BICOUNTS][tags[i]] = {}
                        data[TAG_BICOUNTS][tags[i]][tags[i + 1]] = 1
                else: # is last word
                    data[TAG_BICOUNTS][END_TAG][tags[i]] = data[TAG_BICOUNTS][END_TAG].get(tags[i], 0) + 1
        data[TAG_COUNTS][START_TAG] = len(lines)
        data[TAG_COUNTS][END_TAG] = len(lines)
        # add-one smoothing for tag bigrams
        # assumes first_tag includes all tags
        # todo: add unseen first_tag
        for first_tag in data[TAG_BICOUNTS]: # seen tag bigrams
            data[TAG_BICOUNT_PROBS][first_tag] = {}
            for second_tag in data[TAG_BICOUNTS][first_tag]:
                data[TAG_BICOUNT_PROBS][first_tag][second_tag] = math.log(((data[TAG_BICOUNTS][first_tag][second_tag] + 1)/(data[TAG_COUNTS][first_tag] + NUM_PENN_TAGS)), 10)
        for first_tag in data[TAG_BICOUNTS]: # unseen tag bigrams
            for second_tag in TAGS:
                if second_tag not in data[TAG_BICOUNTS][first_tag]:
                    data[TAG_BICOUNT_PROBS][first_tag][second_tag] = math.log(((1)/(data[TAG_COUNTS][first_tag] + NUM_PENN_TAGS)), 10)
        # add-one smoothing for word-tag bigrams
        for word in data[WORD_COUNTS]: # seen word-tags
            data[WORD_TAG_PROBS][word] = {}
            for tag in TAGS:
                if tag in data[WORD_TAG_COUNTS][word]:
                    data[WORD_TAG_PROBS][word][tag] = math.log(((data[WORD_TAG_COUNTS][word][tag] + 1)/(data[TAG_COUNTS][tag] + NUM_PENN_TAGS)), 10)
                else:
                    data[WORD_TAG_PROBS][word][tag] = math.log((1/(data[TAG_COUNTS][tag] + NUM_PENN_TAGS)), 10)
        data[WORD_TAG_PROBS][UNK] = {} # unseen word-tags
        for tag in TAGS:
            data[WORD_TAG_PROBS][UNK][tag] = math.log((1/(data[TAG_COUNTS][tag] + NUM_PENN_TAGS)), 10)

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
