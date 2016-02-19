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
# import InputDevice, ecodes

# This should be the path to the current directory
base = os.path.dirname(os.path.realpath(__file__))

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
    words.append(filtered)

# We only want the most frequent words
# wbL is a dictionary mapping word lengths to a list of words of that length
# lprobs is a dictionary mapping word names to empirical probabilities
counts = collections.Counter()
pcounts = collections.Counter()
lcounts = collections.Counter()

for word in words:
    counts[word] += 1

pruned = []
for word in words:
    if counts[word] > 1:
        pruned.append(word)
        pcounts[word] = counts[word]

wbL = {}

for word in pruned:
    if len(word) not in wbL:
        wbL[len(word)] = set()

    wbL[len(word)].add(word)

    for w in word:
        lcounts[w] += 1.0

# wprobs is word probabilty given word length
wprobs = {}

for length in wbL:
    wprobs[length] = {}

    totalWs = 0.0
    for w in wbL[length]:
        totalWs += pcounts[w]

    for w in wbL[length]:
        wprobs[length][w] = pcounts[w] / totalWs

# unconditional letter probabilities
lprobs = {}

totals = sum(lcounts.values())
for l in lcounts:
    lprobs[l] = lcounts[l] / totals

print "Setting up keyboard"

lLetters = ['qwert',
            'asdfg',
            'zxcvb']

rLetters = ['yuiop',
            'hjkl',
            'nm']

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

#print lLetterMeans
#print rLetterMeans

#dists2 = {}

#for (letter0, ux0, uy0), (letter1, ux1, uy1) in itertools.product(letter_means, repeat = 2):
#    dists2[(letter0, letter1)] = scipy.stats.multivariate_normal([ux1 - ux0, uy1 - uy0], [[0.2**2, 0.0], [0.0, 0.2**2]])
def classify1(presses):
    if len(presses) < 1:
        return ''

    lps = []
    for side, (x, y) in presses:
        #print dists1[side].keys(), x, y
        # Evaluate letter distributions
        results = [(key, dists1[side][key].pdf([x, y])) for key in dists1[side]]
        
        #print [l for l, p in sorted(results, key = lambda x : x[1], reverse = True)]
        #print '-----'

        totalP = sum([p for l, p in results])

        # For each press, save dictionary matching probability of each letter
        lps.append(dict([(l, -numpy.log(p / totalP)) for l, p in results]))

    tws = []
    for w in wbL[len(presses)]:
        total = 0.0
        for i in range(len(w)):
            if w[i] in lps[i]:
                total += lps[i][w[i]]  # + -numpy.log(lprobs[l])
            else:
                total += 50000.0

        tws.append((w, total))# - numpy.log(wprobs[len(presses)][w])

    tws = sorted(tws, key = lambda x : x[1])

    return tws[0][0]#[w for w, p in tws[0:10]]

print "\nStart typing:"
peaks = []
last = None
startl = None
starth = None
    
ts = []
rs = []
xs = []
ys = []
ps = []

presses = []

lastWord = 0
words = []
#printWords = []

lastP = 0
lastX = 0
lastY = 0

getOut = False

lastClass = 0

lastLpad = False
lastRpad = False
lastBbutton = False
lastAbutton = False

lpadSamples = []
rpadSamples = []

def handle(_, sci):
    #print sci
    global lastWord
    global presses
    global words
    global lastLpad
    global lastRpad
    global lastBbutton
    global lastAbutton
    global lpadSamples
    global rpadSamples
    
    lpad = bool(steamcontroller.SCButtons.LPADTOUCH.value & sci.buttons)
    rpad = bool(steamcontroller.SCButtons.RPADTOUCH.value & sci.buttons)
    bbutton = bool(steamcontroller.SCButtons.B.value & sci.buttons)
    abutton = bool(steamcontroller.SCButtons.A.value & sci.buttons)
    xbutton = bool(steamcontroller.SCButtons.X.value & sci.buttons)

    if xbutton:  # Escape
        raise KeyboardInterrupt
    elif lastAbutton == False and abutton == True:  # Space
        if lastWord != len(presses):
            words.append((lastWord, len(presses) - lastWord))

            lastWord = len(presses)

            sys.stdout.write(' ')
            sys.stdout.flush()
    elif lastBbutton == False and bbutton == True:
        if len(presses) > lastWord:
            presses.pop()

            #print len(presses), lastWord, 'a'

            sys.stdout.write("\b" * (len(presses) - lastWord + 1))
            sys.stdout.write(" " * (len(presses) - lastWord + 1) )
            sys.stdout.write("\b" * (len(presses) - lastWord + 1) )
            sys.stdout.write(classify1(presses[lastWord : len(presses)]))
            sys.stdout.flush()
            #results = classify(ts, xs, ys, ps)

    if lpad:
        lpadSamples.append(((sci.lpad_x + 20000.0) / 40000.0, 1.0 - (sci.lpad_y + 20000.0) / 40000.0))
        
    if rpad:
        rpadSamples.append(((sci.rpad_x + 20000.0) / 40000.0, 1.0 - (sci.rpad_y + 20000.0) / 40000.0))

    if lastLpad and lpad == False:
        presses.append((0, numpy.mean(lpadSamples, axis = 0)))
        lpadSamples = []

        #print len(presses), lastWord, 'b'

        sys.stdout.write("\b" * (len(presses) - lastWord - 1) )
        sys.stdout.write(classify1(presses[lastWord : len(presses)]))
        sys.stdout.flush()
        
    if lastRpad and rpad == False:
        presses.append((1, numpy.mean(rpadSamples, axis = 0)))
        rpadSamples = []

        #print len(presses), lastWord, 'c'
        
        sys.stdout.write("\b" * (len(presses) - lastWord - 1))
        sys.stdout.write(classify1(presses[lastWord : len(presses)]))
        sys.stdout.flush()

        
    lastBbutton = bbutton
    lastAbutton = abutton
    lastLpad = lpad
    lastRpad = rpad

    #print lastWord, len(presses)

try:
    sc = steamcontroller.SteamController(callback = handle)
    sc.run()
except KeyboardInterrupt:
    pass
except Exception as e:
    print str(e)
    

