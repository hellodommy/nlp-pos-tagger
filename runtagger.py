# python3.8 runtagger.py <test_file_absolute_path> <model_file_absolute_path> <output_file_absolute_path>

import os
import math
import sys
import datetime
import json

WORD_COUNTS = 'WORD_COUNTS'
TAG_COUNTS = 'TAG_COUNTS'
TAG_BICOUNTS = 'TAG_BICOUNTS'  # P(t(i-1), t(i))
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

class WordToken:
    def __init__(self, word):
        self.word = word
        self.transition_probs = {}
        self.state_obs_likelihoods = {}

def tag_sentence(test_file, model_file, out_file):
    # write your code here. You can add functions as well.
    with open(model_file, 'r') as rf:
        data = json.loads(rf.read())
    with open(test_file) as rf:
        lines = rf.readlines()
        for line in lines:
            words = line.rstrip().split(' ')
            word_tokens = []
            backpointers = []
            for word in words:
                if word in data[WORD_COUNTS]:
                    word_tokens.append(WordToken(word))
                else:
                    word_tokens.append(WordToken(UNK))
            # init
            for tag in TAGS:
                word_tokens[0].transition_probs[tag] = data[TAG_BICOUNT_PROBS][START_TAG][tag] + data[WORD_TAG_PROBS][word_tokens[0].word][tag]
            for i in range(1, len(word_tokens)):
                curr_word = word_tokens[i].word
                curr_backpointers = dict.fromkeys(TAGS)
                for tag in TAGS:
                    best_prob, best_tag = get_max(tag, word_tokens[i - 1].transition_probs, data[TAG_BICOUNT_PROBS])
                    word_tokens[i].transition_probs[tag] = best_prob + data[WORD_TAG_PROBS][curr_word][tag]
                    curr_backpointers[tag] = best_tag
                backpointers.append(curr_backpointers)
            
    print('Finished...')

def get_max(curr_tag, prev_dict, tag_bicount_probs):
    best_prob = sys.maxsize # probabiltiy for the best path
    best_tag = ""
    for prev_tag in TAGS:
        curr_prob = prev_dict[prev_tag] + tag_bicount_probs[prev_tag][curr_tag]
        if curr_prob < best_prob:
            best_prob = curr_prob
            best_tag = prev_tag
    return best_prob, best_tag

if __name__ == "__main__":
    # make no changes here
    test_file = sys.argv[1]
    model_file = sys.argv[2]
    out_file = sys.argv[3]
    start_time = datetime.datetime.now()
    tag_sentence(test_file, model_file, out_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
