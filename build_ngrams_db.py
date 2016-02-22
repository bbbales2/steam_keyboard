#%%

import json
import os
import collections
import numpy

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    os.chdir('/home/bbales2/steam_keyboard')

f = open('google-books-common-words.txt')

unigrams = collections.Counter()

bigrams = collections.Counter()

stems = {}

words = set()

for i, line in enumerate(f):
    line = line.strip()

    if len(line) == 0:
        break

    word, count = line.split()
    count = int(count)

    for w in word:
        unigrams[w.lower()] += count

    for b in zip(word[:-1], word[1:]):
        bigrams[''.join(b).lower()] += count

    if len(word) not in stems:
        stems[len(word)] = set()

    for i in range(len(word)):
        stems[len(word)].add(word[0 : i + 1].lower())

    words.add(word.lower())

unigrams2 = {}
totalUni = sum(unigrams.values()) * 1.0
for letter, count in sorted(unigrams.items(), key = lambda x : x[1]):
    unigrams2[letter] = -numpy.log(count / totalUni)
    print letter, -numpy.log(count / totalUni)

bigrams2 = {}
totalBi = sum(bigrams.values()) * 1.0
for letters, count in sorted(bigrams.items(), key = lambda x : x[1]):
    bigrams2[letters] = -numpy.log(count / totalBi)
    print letters, -numpy.log(count / totalBi)

stems2 = {}
for length in stems:
    stems2[length] = list(stems[length])

f.close()

f = open('ngrams_db.txt', 'w')
pickle.dump((unigrams2, bigrams2, stems2), f)
f.close()