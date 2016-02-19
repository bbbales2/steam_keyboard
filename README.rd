# Introduction

This is a prototype keyboard for a Steam controller. The idea is to use some basic statistics to make touch typing a lot easier. When I'm playing games and my buddies send me messages, I want to be able to respond easily without going for the keyboard.

It's not gonna work for stuff like typing in passwords or usernames, but I think it'd work for communication pretty well.

# Installing & Running

This requires Ubuntu, a steam controller, and a copy of Stanley Marcel's excellent Steam controller API (https://github.com/ynsta/steamcontroller)

If you have all those things, just run the script:

    python steam_keyboard.py

On the first run it will download a copy of Bram Stoker's Dracula from Gutenberg (http://www.gutenberg.org/ebooks/345). This is used as a reference dictionary. If you want to type a word, it better be in that book (otherwise the controller won't know it exists).

# How it works

This software maps keys onto the Steam Controller touchpad. The idea is that instead of every press corresponding to exactly one key on the keyboard, each press corresponds to a probability of pressing any key. The keys that are closest to the actual press point are given higher probability.

If N keys are pressed, then the software expects the user is looking for an N letter word. Given the presses (each corresponding to a probability for every letter on the keyboard) the keyboard looks in its dictionary for the word with the highest probability (assuming the probability of a word is the product of probabilities of each of its letters).

So if we pressed 4 keys and we want to compute the probability of 'frog' we do:

    p(frog) = p(first press is an f) * p(second press is an r) * p(third press is an o) * p(fourth press is a g)

Since the Steam controller has two touchpads, the keyboard is split like one of those Microsoft keyboads (https://www.microsoft.com/accessories/en-us/products/keyboards/natural-ergonomic-keyboard-4000/b2m-00012).

The probabilities are computed with Gaussians. So each key is mapped onto a position on the controller, and each time a button is pressed the probability for a certain letter is proportional too:

    exp(-(press_position - letter_position)**2 / (2 * sigma^2))

Keys don't blur across touchpads. If you want to press a key on the left side of the Microsoft keyboard, you gotta press the left touchpad.
