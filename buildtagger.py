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
END_TAG_COUNTS = 'END_TAG_COUNTS' # P(</s>|tT)

data = {}
data[WORD_COUNTS] = {}
data[TAG_COUNTS] = {}
data[TAG_BICOUNTS] = {}
data[WORD_TAG_COUNTS] = {}
data[END_TAG_COUNTS] = {}

def train_model(train_file, model_file):
    # write your code here. You can add functions as well.

    with open(train_file) as rf:
        lines = rf.readlines()
        for line in lines:
            words_with_tags = line.rstrip().split(' ')
            words = [word_with_tag.rsplit('/', 1)[0].lower()
                     for word_with_tag in words_with_tags]
            tags = [word_with_tag.rsplit('/', 1)[1]
                     for word_with_tag in words_with_tags]
            for i in range(len(words_with_tags)):
                data[WORD_COUNTS][words[i]] = data[WORD_COUNTS].get(words[i], 0) + 1
                data[TAG_COUNTS][tags[i]] = data[TAG_COUNTS].get(tags[i], 0) + 1
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
                    data[END_TAG_COUNTS][tags[i]] = data[END_TAG_COUNTS].get(tags[i], 0) + 1
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
