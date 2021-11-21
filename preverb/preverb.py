#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

"""
An emtsv module to connect preverbs to the verb or verb-derivative
token to which they belong.
"""

import json
from word import Word

from itertools import chain
from more_itertools import split_at, windowed

ENV = 2 # search for [/Prev] in a -env..env environment of the [/V]

VERB_POSTAG = '[/V]'
PREVERB_POSTAG = '[/Prev]'
ADVERB_POSTAG = '[/Adv]'


class Preverb:
    '''Required by xtsv.'''

    def __init__(self, *_, source_fields=None, target_fields=None):
        """
        Required by xtsv.
        Initialise the module.
        """
        # Tudom, hogy ezeket elvileg a source_fields és a target_fields
        # adná át, de nem látom be, hogy miért kellene fájlok között ugrálnom,
        # hogy megtudjam, mik a használt mezők, ezért csak azért is így
        # inicializálom őket.
        self.source_fields = {'anas', 'xpostag', 'lemma'}
        self.target_fields = ['separated', 'previd']
        self.prev_id = 0
        self.window_size = 2 * ENV + 1
        self.center = ENV # index of central element in window

    def process_sentence(self, sen, _):
        """
        Required by xtsv.
        Process one sentence per function call.
        :return: sen object augmented with output field values for each token
        """

        word_objects = [Word(tok + ['', '']) for tok in sen]

        padded_sentence = chain(self.padding, word_objects, self.padding) # !

        processed = []


        for window in windowed(padded_sentence, self.window_size): # !

            left = list(reversed(window[:self.center + 1])) # abc..
            central = window[self.center]                   # ..c..
            right = window[self.center:]                    # ..cde

            if (central.xpostag.startswith(VERB_POSTAG)
                    and VERB_POSTAG in central.anas  # is it a verb according to anas?
                    and central.form != "volna"):

                # Case 1: already contains a preverb
                if (PREVERB_POSTAG in central.anas and
                    contains_preverb(central)):
                        self.add_preverb(central)

                # Case 2: "szét" [msd="IGE.*|HA.*"] [msd="IGE.*" & word != "volna"]
                # szét kell szerelni, szét se szereli
                elif (left[2].xpostag == PREVERB_POSTAG and
                      left[1].xpostag.startswith((ADVERB_POSTAG, VERB_POSTAG))):
                    self.add_preverb(central, left[2])

                # Case 3: [msd="IGE.*" & word != "volna] "szét"
                elif right[1].xpostag == PREVERB_POSTAG:
                    self.add_preverb(central, right[1])

                # Case 4: [msd="IGE.*" & word != "volna] [msd="HA.*" | word="volna"] "szét"
                # rágja is szét, rágta volna szét, tépi hirtelen szét
                elif (right[2].xpostag == PREVERB_POSTAG and
                        (right[1].xpostag.startswith(ADVERB_POSTAG)
                         or right[1].form == 'volna')
                      ):
                    self.add_preverb(central, right[2])

                # Doesn't have a preverb
                else:
                    pass

            # should be collected before printing
            # because left[2] can change if it is a preverb!
            processed.append(central)

        return [str(word).split('\t') for word in processed]

    def prepare_fields(self, field_names):
        """
        Required by xtsv.
        :param field_names: the dictionary of the names of the input fields
        :return: the list of the initialised feature classes as required for
                process_sentence
        """
        column_count = len(field_names) // 2
        fields = [field_names[i] for i in range(column_count)]

        Word.features = fields
        fakeword = Word([''] * len(Word.features))
        self.padding = [fakeword] * ENV

        self.compound_exists = 'compound' in fields
        return fields

    def add_preverb(self, verb, preverb=None):
        """Update *verb* with info from *preverb*."""
        verb.xpostag = PREVERB_POSTAG + verb.xpostag
        if preverb is not None:
            vlemma = verb.lemma.lower()

            self.prev_id += 1
            previd = str(self.prev_id)

            # handle verb
            verb.lemma = preverb.lemma + vlemma
            if self.compound_exists:
                verb.compound = preverb.lemma + '#' + vlemma
            verb.separated = 'sep'
            verb.previd = previd

            # handle preverb

            # TODO: Nem látom át, hogy hogy kezeli az xtsv a
            # parancssori argumentumokat, és ezt most nincs is
            # időm kibogarászni, ezért ezt a feltételt ideiglegesen
            # kiveszem, majd vissza kell tenni úgy, hogy jó legyen.
#            if args.add_verb_lemma:
#               preverb.lemma += '[' + vlemma + ']'
#            else:
                # empty lemma for connected preverb
            preverb.lemma = ''

            if self.compound_exists:
                preverb.compound = preverb.lemma
            preverb.separated = 'conn'
            preverb.previd = previd
        else:
            verb.separated = 'pfx'


def contains_preverb(verb):
    """
    Check whether the verb form contains a preverb according to
    the analysis selected by the pos tagger.
    """
    anas_list = json.loads(verb.anas)
    for ana in anas_list:
        if ana["lemma"] == verb.lemma and ana["tag"] == verb.xpostag:
            last_good_ana = ana
    return PREVERB_POSTAG in last_good_ana['readable']
