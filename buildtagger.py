# python3.8 buildtagger.py <train_file_absolute_path> <model_file_absolute_path>

import os
import math
import sys
import datetime

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

    with open(train_file) as f:
        lines = f.readlines();
        for line in lines:
            words_with_tags = line.split(' ')
            words = [word_with_tag.rsplit('/', 1)[0].lower()
                     for word_with_tag in words_with_tags]
            tags = [word_with_tag.rsplit('/', 1)[1]
                     for word_with_tag in words_with_tags]
            for i in range(len(words_with_tags) - 1):
                data[WORD_COUNTS][words[i]] = data[WORD_COUNTS].get(words[i], 0) + 1
                data[TAG_COUNTS][tags[i]] = data[TAG_COUNTS].get(tags[i], 0) + 1
                if words[i] in data[WORD_TAG_COUNTS]:
                    data[WORD_TAG_COUNTS][words[i]][tags[i]] = data[WORD_TAG_COUNTS][words[i]].get(tags[i], 0) + 1
                else:
                    data[WORD_TAG_COUNTS][words[i]] = {}
                    data[WORD_TAG_COUNTS][words[i]][tags[i]] = 1
        print(data[WORD_TAG_COUNTS])
    print('Finished...')

if __name__ == "__main__":
    # make no changes here
    train_file = sys.argv[1]
    model_file = sys.argv[2]
    start_time = datetime.datetime.now()
    train_model(train_file, model_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
