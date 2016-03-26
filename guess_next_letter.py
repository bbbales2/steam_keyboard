#%%

import scipy.interpolate
import numpy
import matplotlib.pyplot as plt
import scipy.cluster
import collections
import select
import itertools
import nltk
import re
import os
import sys
# import InputDevice, ecodes

os.chdir('/home/bbales2/steam_keyboard')
# This should be the path to the current directory
base = '/home/bbales2/steam_keyboard'

if not os.path.exists(os.path.join(base, '345.txt')):
    import urllib2
    print "Corpora doesn't exist... Downloading {0}".format('http://www.gutenberg.org/ebooks/345.txt.utf-8')
    url = urllib2.urlopen('http://www.gutenberg.org/ebooks/345.txt.utf-8')
    f = open(os.path.join(base, '345.txt'), 'w')
    f.write(url.read())
    f.close()
    print "Download finished"

print "Building dictionary"
sys.stdout.flush()

#Import our dictionary
f = open(os.path.join(base, '345.txt'))
data = unicode(f.read(), 'utf-8')
#print data
tokens = nltk.word_tokenize(data)
f.close()

words = []
clear = re.compile('[^A-Za-z]')
number = re.compile('[0-9]')

# We only want letters
# Get rid of words with any numbers
# Delete any other errant characters
for token in tokens:
    if number.match(token):
        continue

    filtered = clear.sub('', token).lower()

    if len(filtered) > 0:
        words.append(filtered)
import os

#%%

def one(N, i):
    out = numpy.zeros(N)
    out[i] = 1
    return out

#%%

string = ' '.join(words)[:10000]

tokens1 = 'abcdefghijklmnopqrstuvwxyz '
tokens2 = [a + b for a, b in list(itertools.product(tokens1, repeat = 2))]

string += tokens1

idxs1 = dict([(t, i) for i, t in enumerate(tokens1)])
idxs2 = dict([(t, i) for i, t in enumerate(tokens2)])

enc1 = dict([(t, one(len(tokens1), i)) for i, t in enumerate(tokens1)])
enc2 = dict([(t, one(len(tokens2), i)) for i, t in enumerate(tokens2)])

s2buttonsR = ['asq', 'wer', 'dfgt', 'zxcv', 'yhj', 'uio', 'klp', 'bnm', ' ']

s2buttons = {}
s2buttonsIdxs = {}
s2buttonsEnc = {}
for i, letters in enumerate(s2buttonsR):
    s2buttonsIdxs[i] = i
    s2buttonsEnc[i] = one(len(s2buttonsR), i)

    for l in letters:
        s2buttons[l] = i

buttons = [s2buttons[s] for s in string]

string = '  ' + string

inputs = []
for c, s1, s2, bn, b0, b1, b2 in zip(string[2:], string[:-3], string[1:-2], [s2buttons[' ']] + [s2buttons[' ']] + buttons[:-3], [s2buttons[' ']] + buttons[:-2], buttons[:-1], buttons[1:]):
    #print s1, s2, benc1[s1],
    inputs.append(numpy.concatenate((s2buttonsEnc[bn], s2buttonsEnc[b0], s2buttonsEnc[b1])))#numpy.concatenate((s2buttonsEnc[b0], s2buttonsEnc[b1])))#, s2buttonsEnc[b2])))

inputs = numpy.array(inputs)

outputs = []
for s in string[2:-1]:
    outputs.append(idxs1[s])

outputs = numpy.array(outputs)

#%%
from pystruct.models import ChainCRF
from pystruct.learners import FrankWolfeSSVM
#%%
import sklearn.linear_model
import sklearn.cross_validation
import sklearn.ensemble

Xtrain, Xtest, Ytrain, Ytest = sklearn.cross_validation.train_test_split(inputs, outputs)
#
lr = sklearn.linear_model.LogisticRegression()
#lr = sklearn.ensemble.RandomForestClassifier()

sklearn.cross_validation.cross_val_score(lr, inputs, outputs)
#%%
lr.fit(inputs, outputs)
#%%
string2 = ' '.join(words)[10000:10050]

buttons2 = [s2buttons[s] for s in string2]

string2 = '  ' + string2

inputs2 = []
outputs2 = ''
cls = ''
#enc1[s1],
for c, s1, s2, bn, b0, b1, b2 in zip(string2[2:], string2[:-3], string2[1:-2], [s2buttons[' ']] + [s2buttons[' ']] + buttons[:-3], [s2buttons[' ']] + buttons[:-2], buttons2[:-1], buttons2[1:]):#, enc1[s2]
    vector = numpy.array(numpy.concatenate((s2buttonsEnc[bn], s2buttonsEnc[b0], s2buttonsEnc[b1], s2buttonsEnc[b2])))#, s2buttonsEnc[b2])))
    #print s1, s2, b1, b2
    out = lr.coef_.dot(vector) + lr.intercept_.transpose()
    #out = lr.predict_log_proba(vector).flatten()
    #print numpy.argmax(out), lr.predict(vector[:, 0])[0]

    computed = [(tokens1[o], '{:0.3f}'.format(out[o]), o) for o in numpy.argsort(-out.flatten())][0:3]

    tokens = [s2buttons[a] for a, b, c, in computed]
   #for token, score, idx in computed:

    if tokens[0] != b1:
        print 'Hiiiiiiii'

    print c, b1, computed, tokens

    #outputs2 += tokens1[lr.predict(vector[:, 0])[0]]
    outputs2 += tokens1[numpy.argmax(out)]
    cls += str(numpy.argmax(out))

print string2[2:]
print outputs2
print cls
#%%
plt.imshow(lr.coef_, interpolation = 'NONE')
plt.show()
#%%
vector = numpy.array(numpy.concatenate((enc1['i'], enc1['t'], s2buttonsEnc[8], s2buttonsEnc[4])))
out = lr.coef_.dot(vector) + lr.intercept_.transpose()

print c, b1, [(tokens1[o], out[o], o) for o in numpy.argsort(-out.flatten())][0:3]
