import steamcontroller

# This is basically one of Stany's scripts

# The MIT License (MIT)
#
# Copyright (c) 2015 Stany MARCEL <stanypub@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import json

if len(sys.argv) != 2:
    print "This program takes exactly one argument: ./record.py file_to_record_to"
    exit(0)

recording = []

def record(_, sci):
    print sci

    global recording

    recording.append({
        'status' : int(sci.status),
        'seq' : int(sci.seq),
        'buttons' : int(sci.buttons),
        'ltrig' : int(sci.ltrig),
        'rtrig' : int(sci.rtrig),
        'lpad_x' : int(sci.lpad_x),
        'lpad_y' : int(sci.lpad_y),
        'rpad_x' : int(sci.rpad_x),
        'rpad_y' : int(sci.rpad_y)
    })

try:
    sc = steamcontroller.SteamController(callback = record)
    sc.run()
except KeyboardInterrupt:
    pass
except Exception as e:
    print str(e)

f = open(sys.argv[1], 'w')
json.dump(recording, f)
f.close()
