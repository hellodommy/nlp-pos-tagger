# python3.8 runtagger.py <test_file_absolute_path> <model_file_absolute_path> <output_file_absolute_path>

import os
import math
import sys
import datetime
import json

WORD_TAG_PROBS = 'WORD_TAG_PROBS'
TAG_TAG_PROBS = 'TAG_TAG_PROBS'
CAP_INITIAL_PROBS = 'CAP_INITIAL_PROBS'
HYPH_PROBS = 'HYPH_PROBS'
SUFFIX_PROBS = 'SUFFIX_PROBS'
UNKNOWN_PROBS = 'UNKNOWN_PROBS'  # P(unknown word|t)
START_TAG = '<start>'
END_TAG = '</end>'
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

SUFFIXES = ["age", "al", "ance", "ence", "dom", "ee", "er", "or", "hood", "ism", "ist", "ity", "ty", "ment", "ness", "ry", "ship", "sion", "tion", "xion", "able", "ible", "al", "en", "ese", "ful", "i", "ic", "ish", "ive", "ian", "less", "ly", "ous", "y", "ate", "en", "ify", "ize", "ise", "ward", "wards", "wise", "s", "ed", "ing"]

data = {}

class WordToken:
    def __init__(self, word):
        self.word = word
        self.probs = {}
        self.backpointers = {}

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
                word_tokens.append(WordToken(word))
            # init
            for tag in data[TAG_TAG_PROBS][START_TAG]:
                first_word = word_tokens[0].word.lower()
                if first_word in data[WORD_TAG_PROBS]:
                    if tag in data[WORD_TAG_PROBS][first_word]:
                        word_tokens[0].probs[tag] = data[TAG_TAG_PROBS][START_TAG][tag] + data[WORD_TAG_PROBS][first_word][tag]
                else: # we need P(unknownword|tag)
                    unknown_prob = get_unknown_prob(tag, word_tokens[0].word, data)
                    if unknown_prob != 0:
                        word_tokens[0].probs[tag] = unknown_prob
            # recursive step
            for i in range(1, len(word_tokens)):
                curr_word = word_tokens[i].word.lower()
                for curr_tag in TAGS:
                    max_prob, max_tag = get_max(curr_tag, word_tokens[i-1], data[TAG_TAG_PROBS])
                    if max_tag != "": # P(curr_tag|prev_tag) is seen
                        word_tokens[i].backpointers[curr_tag] = max_tag
                        if curr_word in data[WORD_TAG_PROBS]:
                            if curr_tag in data[WORD_TAG_PROBS][curr_word]:
                                word_tokens[i].probs[curr_tag] = max_prob + data[WORD_TAG_PROBS][curr_word][curr_tag]
                        else:
                            unknown_prob = get_unknown_prob(curr_tag, word_tokens[i].word, data)
                            if unknown_prob != 0:
                                word_tokens[i].probs[curr_tag] = max_prob + unknown_prob
                if not word_tokens[i].probs: # special case where no POS tag can be associated with this word
                    if curr_word in data[WORD_TAG_PROBS]:
                        max_prob, max_tag = get_max_lenient(False, curr_word, word_tokens[i - 1], data)
                    else:
                        max_prob, max_tag = get_max_lenient(True, curr_word, word_tokens[i - 1], data)
                    if max_tag != "":
                        word_tokens[i].probs[curr_tag] = max_prob
                        word_tokens[i].backpointers[curr_tag] = max_tag
            # terminating
            max_prob, max_tag = get_max(END_TAG, word_tokens[len(word_tokens) - 1], data[TAG_TAG_PROBS])
            best_tags = []
            curr_backpointer = max_tag
            for i in range(len(word_tokens) - 1, 0, -1):
                best_tags.append(curr_backpointer)
                curr_backpointer = word_tokens[i].backpointers[curr_backpointer]
            best_tags.append(curr_backpointer)
            best_tags.reverse()
            # appending tag to sentence
            tagged_sentence = ""
            for i in range(len(word_tokens)):
                tagged_sentence = tagged_sentence + word_tokens[i].word + "/" + best_tags[i] + " "
            tagged_sentence = tagged_sentence + "\n"
            with open(out_file, 'a') as wf:
                wf.write(tagged_sentence)
    print('Finished...')

# In case none of the curr word's seen tags occur with the previous tag
# Then we multiply by P(curr word|tag) only to determine the best prev tag
# and the probability for the current cell
def get_max_lenient(is_unknown, curr_word, prev_word_token, data):
    max_prob = - sys.maxsize - 1
    max_tag = ""
    if is_unknown:
        for prev_tag in prev_word_token.probs:
            for tag in data[UNKNOWN_PROBS]:
                curr_prob = prev_word_token.probs[prev_tag] + get_unknown_prob(tag, curr_word, data)
                if curr_prob > max_prob:
                    max_prob = curr_prob
                    max_tag = prev_tag
    else:
        for prev_tag in prev_word_token.probs:
            for curr_tag in data[WORD_TAG_PROBS][curr_word]:
                curr_prob = prev_word_token.probs[prev_tag] + data[WORD_TAG_PROBS][curr_word][curr_tag]
                if curr_prob > max_prob:
                    max_prob = curr_prob
                    max_tag = prev_tag
    return max_prob, max_tag

def get_max(curr_tag, prev_word_token, tag_tag_probs):
    max_prob = - sys.maxsize - 1
    max_tag = ""
    for prev_tag in prev_word_token.probs:
        if curr_tag in tag_tag_probs[prev_tag]:
            curr_prob = prev_word_token.probs[prev_tag] + tag_tag_probs[prev_tag][curr_tag]
            if curr_prob > max_prob:
                max_prob = curr_prob
                max_tag = prev_tag
    return max_prob, max_tag

def get_unknown_prob(tag, word, data):
    unknown_prob = 0
    if word.istitle():
        unknown_prob += data[CAP_INITIAL_PROBS].get(tag, 0)
    word = word.lower()
    if tag in data[UNKNOWN_PROBS]:
        unknown_prob += data[UNKNOWN_PROBS][tag]
    for suffix in SUFFIXES:
        if word.endswith(suffix):
            unknown_prob += data[SUFFIX_PROBS][suffix].get(tag, 0)
            break
    if HYPHEN in word:
        unknown_prob += data[HYPH_PROBS].get(tag, 0)
    return unknown_prob

if __name__ == "__main__":
    # make no changes here
    test_file = sys.argv[1]
    model_file = sys.argv[2]
    out_file = sys.argv[3]
    start_time = datetime.datetime.now()
    tag_sentence(test_file, model_file, out_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
