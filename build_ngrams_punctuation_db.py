#%%

import os
import collections
import numpy
import nltk
import pickle

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    os.chdir('/home/bbales2/steam_keyboard')

reuters = nltk.corpus.gutenberg.raw()
words = nltk.corpus.gutenberg.words()
#%%
unigrams = collections.Counter()

bigrams = collections.Counter()

stems = {}

import time
tmp = time.time()
for i in range(len(reuters) - 1):
    unigrams[reuters[i].lower()] += 1
    bigrams[reuters[i : i + 2].lower()] += 1

unigrams[reuters[-1]] += 1

for word in words:
    if len(word) not in stems:
        stems[len(word)] = set()

    for i in range(len(word)):
        stems[len(word)].add(word[0 : i + 1].lower())
print time.time() - tmp
#%%

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

f = open('ngrams_db.txt', 'w')
pickle.dump((unigrams2, bigrams2, stems), f)
f.close()