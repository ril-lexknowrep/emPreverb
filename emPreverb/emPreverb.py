#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

"""
An emtsv module to connect preverbs to the verb or verb-derivative
token to which they belong.
"""

import json

from itertools import chain
from more_itertools import split_at, windowed

from types import SimpleNamespace


ENV = 3 # search for [/Prev] in a -env..env environment of the [/V]

VERB_POSTAG = '[/V]'
PREVERB_POSTAG = '[/Prev]'
ADVERB_POSTAG = '[/Adv]'
ADVERBIAL_PRONOUN_POSTAG = '[/Adv|Pro]'
ADJECTIVE_POSTAG = '[/Adj]'
INFINITIVE_POSTAG = '[/V][Inf'  # nem hiányzik a végéről semmi!
NOUN_POSTAG = '[/N]'
QUESTION_PARTICLE_POSTAG = '[/QPtcl]'
DET_PRO_POSTAG = '[/Det|Pro]'
N_PRO_POSTAG = '[/N|Pro]'
MODAL_PARTICIPLE_MORPHEME = '[_ModPtcp/Adj]'
PERFECT_PARTICIPLE_MORPHEME = '[_PerfPtcp/Adj]'
IMPERFECT_PARTICIPLE_MORPHEME = '[_ImpfPtcp/Adj]'
ADVERBIAL_PARTICIPLE_MORPHEME = '[_AdvPtcp/Adv]'
FUTURE_PARTICIPLE_MORPHEME = '[_FutPtcp/Adj]'
GERUND_MORPHEME = '[_Ger/N]'
CONTRAST_PARTICLES = ['ám', 'viszont', 'azonban'] # [/Cnj]


class Word(SimpleNamespace):
    """
    Convenience class to access predefined word features as attributes.
    Set Word.features = ... before using this class!
    """
    features = []
    def __init__(self, vals):
        if len(vals) != len(self.features):
            raise RuntimeError(
                f"{len(self.features)} values expected, {len(vals)} provided")
        super().__init__(**dict(zip(self.features, vals)))

    def as_list(self): # XXX best practice? can I define list(...) for this class?
        return self.__dict__.values()


class EmPreverb:
    '''Required by xtsv.'''

    def __init__(self, *_, source_fields=None, target_fields=None):
        """
        Required by xtsv.
        Initialise the module.
        """

        # Field names for xtsv (the code below is mandatory for an xtsv module)
        if source_fields is None:
            source_fields = set()

        if target_fields is None:
            target_fields = []

        self.source_fields = source_fields
        self.target_fields = target_fields

        self.prev_id = 0
        self.window_size = 2 * ENV + 1
        self.center = ENV # index of central element in window

    def process_sentence(self, sen, _):
        """
        Required by xtsv.
        Process one sentence per function call.
        :return: sen object augmented with output field values for each token
        """

        word_objects = (Word(
            tok + [''] * len(self.target_fields) # add empty target fields
        ) for tok in sen)
        # we assume that target_fields are NOT among input fields!

        padded_sentence = chain(self.padding, word_objects, self.padding) # !

        processed = []


        for window in windowed(padded_sentence, self.window_size): # !

            left = list(reversed(window[:self.center + 1])) # abc..
            central = window[self.center]                   # ..c..
            right = window[self.center:]                    # ..cde

            if (central.xpostag.startswith(VERB_POSTAG)
                and (ADVERBIAL_PARTICIPLE_MORPHEME in central.anas
                    or central.xpostag.startswith(INFINITIVE_POSTAG))
                and (left[1].xpostag.startswith((ADVERB_POSTAG, ADVERBIAL_PRONOUN_POSTAG, VERB_POSTAG))
                     or left[1].form in CONTRAST_PARTICLES
                     or left[1].xpostag.startswith((DET_PRO_POSTAG, N_PRO_POSTAG)))
                and left[2].xpostag.startswith((ADVERB_POSTAG, ADVERBIAL_PRONOUN_POSTAG, VERB_POSTAG))
                and left[3].xpostag == PREVERB_POSTAG
                ):
                self.add_preverb(central, -3, left[3])

            elif (central.xpostag.startswith(VERB_POSTAG)
                and right[1].xpostag.startswith((ADVERB_POSTAG, ADVERBIAL_PRONOUN_POSTAG))
                and right[2].xpostag.startswith((ADVERB_POSTAG, ADVERBIAL_PRONOUN_POSTAG))
                and right[3].xpostag == PREVERB_POSTAG
                ):
                self.add_preverb(central, 3, right[3])

            elif (
                (central.xpostag.startswith(VERB_POSTAG)
                    and VERB_POSTAG in central.anas  # is it a verb according to anas?
                    and central.form != "volna"
                    and not (right[1].xpostag.startswith(INFINITIVE_POSTAG)
                             or ADVERBIAL_PARTICIPLE_MORPHEME in right[1].xpostag
                             or right[2].xpostag.startswith(INFINITIVE_POSTAG)
                             or ADVERBIAL_PARTICIPLE_MORPHEME in right[2].xpostag))
                or
                (central.xpostag.startswith(ADJECTIVE_POSTAG)
                    and MODAL_PARTICIPLE_MORPHEME in central.anas)
                or
                (central.xpostag == ADVERB_POSTAG
                    and (ADVERBIAL_PARTICIPLE_MORPHEME in central.anas   # Kalivoda (2021: 64-6)
                         or FUTURE_PARTICIPLE_MORPHEME in central.anas)) # Kalivoda (2021: 68-9)
                ):

                # Case 1: already contains a preverb
                if (PREVERB_POSTAG in central.anas and
                    contains_preverb(central)):
                        self.add_preverb(central, 0)

                # Case 2: "szét" [msd="IGE.*|HA.*"] [msd="IGE.*" & word != "volna"]
                # szét kell szerelni, szét se szereli
                elif (left[2].xpostag == PREVERB_POSTAG and
                      left[1].xpostag.startswith((ADVERB_POSTAG, ADVERBIAL_PRONOUN_POSTAG, VERB_POSTAG))):
                    self.add_preverb(central, -2, left[2])

                # Case 3: [msd="IGE.*" & word != "volna] "szét"
                elif right[1].xpostag == PREVERB_POSTAG:
                    self.add_preverb(central, 1, right[1])

                # Case 4: [msd="IGE.*" & word != "volna] [msd="HA.*" | word="volna"] "szét"
                # rágja is szét, rágta volna szét, tépi hirtelen szét
                elif (right[2].xpostag == PREVERB_POSTAG and
                        (right[1].xpostag.startswith((ADVERB_POSTAG, ADVERBIAL_PRONOUN_POSTAG))
                         or right[1].xpostag == QUESTION_PARTICLE_POSTAG
                         or right[1].form == 'volna'
                         or right[1].form in CONTRAST_PARTICLES
                         or right[1].xpostag.startswith((NOUN_POSTAG, DET_PRO_POSTAG, N_PRO_POSTAG))
                         )
                      ):
                    self.add_preverb(central, 2, right[2])

                elif (left[1].xpostag == PREVERB_POSTAG
                      and not left[3].xpostag.startswith(VERB_POSTAG)
                      and not left[2].xpostag.startswith(VERB_POSTAG)
                      and (right[1].form == 'volna' or
                            not right[1].xpostag.startswith(VERB_POSTAG))
                      and not ADVERBIAL_PARTICIPLE_MORPHEME in right[1].anas
                      and not right[2].xpostag.startswith(VERB_POSTAG)
                      and not ADVERBIAL_PARTICIPLE_MORPHEME in right[2].anas
                      and not right[3].xpostag.startswith(VERB_POSTAG)
                      and not ADVERBIAL_PARTICIPLE_MORPHEME in right[3].anas
                      ):
                    self.add_preverb(central, -1, left[1])

                # Doesn't have a preverb
                else:
                    pass

            elif (
                ((central.xpostag.startswith(ADJECTIVE_POSTAG)
                    and (PERFECT_PARTICIPLE_MORPHEME in central.anas
                         or IMPERFECT_PARTICIPLE_MORPHEME in central.anas
                         or FUTURE_PARTICIPLE_MORPHEME in central.anas))
                or
                (central.xpostag.startswith((NOUN_POSTAG,ADJECTIVE_POSTAG))
                    and GERUND_MORPHEME in central.anas))
                and left[2].xpostag == PREVERB_POSTAG
                and left[1].form in ('nem', 'sem', 'se', 'is')):
                    # Kalivoda (2021: 69-73)
                    self.add_preverb(central, -2, left[2])

            # should be collected before printing
            # because left[2] can change if it is a preverb!
            processed.append(central)

        return [word.as_list() for word in processed]

    def prepare_fields(self, field_names):
        """
        Required by xtsv.
        :param field_names: the dictionary of the names of the input fields
        :return: the list of the initialised feature classes as required for
                process_sentence
        """
        field_names = {k: v for k, v in field_names.items() if isinstance(k, str)}
        # target fields are also present!

        # XXX ha az input field-ek között szerepel target field, akkor összezavarodik!
        # -> ez nem általános probléma? ha igen: csináljak xtsv issút belőle!

        # set Word.features for the whole script
        # XXX best practice for this?
        Word.features = field_names.keys()

        fakeword = Word([''] * len(Word.features))
        self.padding = [fakeword] * ENV

        self.compound_exists = 'compound' in Word.features

        # nothing to return -- all are noted in Word
        return None

    def add_preverb(self, verb, prevpos, preverb=None):
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
            verb.prev = 'sep'
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
            preverb.prev = 'conn'
            preverb.previd = previd
            verb.prevpos = "{:+0}".format(prevpos)
        else:
            verb.prev = 'pfx'


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
