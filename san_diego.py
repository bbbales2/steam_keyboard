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
import steamcontroller
import json
import sortedcontainers
import pickle

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    os.chdir('/home/bbales2/steam_keyboard')

print "Setting up keyboard"

lLetters = ['qwert',
            'asdfg',
            'zxcvb']

rLetters = ['yuiop',
            'hjkl',
            'nm',
            ' ']

dx = 1.0 / 6.0

sigma = 0.2

lLetterMeans = []
rLetterMeans = []

for i, row in enumerate(lLetters):
    uy = (i + 1) * 0.25
    for j, letter in enumerate(row):
        ux = i * dx * 0.1 + (j + 1) * dx

        lLetterMeans.append((letter, ux, uy))

for i, row in enumerate(rLetters):
    uy = (i + 1) * 0.25
    for j, letter in enumerate(row):
        ux = i * dx * 0.1 + (j + 1) * dx

        rLetterMeans.append((letter, ux, uy))

dists1 = { 0 : {}, # 0 is for lpresses, 1 is for rpresses!
           1 : {} }

for letter, ux, uy in lLetterMeans:
    dists1[0][letter] = scipy.stats.multivariate_normal([ux, uy], [[sigma**2, 0.0], [0.0, sigma**2]])

for letter, ux, uy in rLetterMeans:
    dists1[1][letter] = scipy.stats.multivariate_normal([ux, uy], [[sigma**2, 0.0], [0.0, sigma**2]])

#%%

f = open('ngrams_db.txt')
unigrams, bigrams, stems = pickle.load(f)
f.close()

#stems2 = {}
#for length in stems:
#    stems2[int(length)] = set(stems[length])
#stems = stems2

#%%

f = open('carmen_san_diego_button.txt')
recorded = json.load(f)
f.close()

#%%

lastClass = 0

lastLpad = False
lastRpad = False
lastBbutton = False
lastAbutton = False

lpadSamples = []
rpadSamples = []

presses = []
lastWord = 0
words = []

def coordsToProbs(side, x, y):
    results = [(key, dists1[side][key].pdf([x, y])) for key in dists1[side]]

    totalP = sum([p for l, p in results])

    # For each press, save dictionary matching probability of each letter
    return sorted([(l, -numpy.log(p / totalP)) for l, p in results], key = lambda x : x[1])

for sci in recorded:
    global lastWord
    global presses
    global words
    global lastLpad
    global lastRpad
    global lastBbutton
    global lastAbutton
    global lpadSamples
    global rpadSamples

    lpad = bool(steamcontroller.SCButtons.LPADTOUCH.value & sci['buttons'])
    rpad = bool(steamcontroller.SCButtons.RPADTOUCH.value & sci['buttons'])
    bbutton = bool(steamcontroller.SCButtons.B.value & sci['buttons'])
    abutton = bool(steamcontroller.SCButtons.A.value & sci['buttons'])
    xbutton = bool(steamcontroller.SCButtons.X.value & sci['buttons'])

    ltrig = sci['ltrig'] / 256.0
    rtrig = sci['rtrig'] / 256.0

    lpadx = (sci['lpad_x'] + 20000.0) / 40000.0
    lpady = 1.0 - (sci['lpad_y'] + 20000.0) / 40000.0

    rpadx = (sci['rpad_x'] + 20000.0) / 40000.0
    rpady = 1.0 - (sci['rpad_y'] + 20000.0) / 40000.0

    if xbutton:  # Escape
        raise KeyboardInterrupt
    elif lastAbutton == False and abutton == True:  # Space
        words.append(presses)

        presses = []

    if lpad:
        lpadSamples.append((lpadx, lpady))

    if rpad:
        rpadSamples.append((rpadx, rpady))

    if lastLpad and lpad == False:
        presses.append(coordsToProbs(0, *numpy.mean(lpadSamples, axis = 0)))
        lpadSamples = []

        #print len(presses), lastWord, 'b'

        #sys.stdout.write("\b" * (len(presses) - lastWord - 1) )
        #sys.stdout.write(classify1(presses[lastWord : len(presses)]))
        #sys.stdout.flush()

    if lastRpad and rpad == False:
        presses.append(coordsToProbs(1, *numpy.mean(rpadSamples, axis = 0)))
        rpadSamples = []

        #print len(presses), lastWord, 'c'

        #sys.stdout.write("\b" * (len(presses) - lastWord - 1))
        #sys.stdout.write(classify1(presses[lastWord : len(presses)]))
        #sys.stdout.flush()


    lastBbutton = bbutton
    lastAbutton = abutton
    lastLpad = lpad
    lastRpad = rpad

words.append(presses[:-1])

#%%

maxc0 = numpy.max(bigrams.values())

def transitionP(base, press, targetLength):
    out = []

    for letter, log in press:
        #log += unigrams[letter]
        if len(base) > 0:
            big = base[-1] + letter
            if big in bigrams:
                log += bigrams[base[-1] + letter]
            else:
                log += maxc0

        if True:#targetLength in stems and base + letter in stems[targetLength]:
            out.append((log, base + letter))

    return out

minc = numpy.min(bigrams.values())

import time

tmp = time.time()
for word in words[:]:
    Q = sortedcontainers.SortedDict()

    Q[0.0] = ''

    maxLen = 0

    iters = 0
    while 1:
        #for i in range(len(Q)):
        if True:
            log = Q.iloc[0]
            base = Q[log]

            #if log + (maxLen - len(base)) * minc

            #print base, log

            if len(base) == len(word):
                print base
                break
            else:
                press = word[len(base)]
                for dlog, new in transitionP(base, press, len(word)):
                    Q[log + dlog] = new
                    iters += 1

                maxLen = max(maxLen, len(new))

                del Q[log]

#Q.items()
    print len(Q), iters
print time.time() - tmp