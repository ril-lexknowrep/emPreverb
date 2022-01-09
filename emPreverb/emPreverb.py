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


ENV = 4 # search for [/Prev] in a -env..env environment of the [/V]

VERB_POSTAG = '[/V]'
PREVERB_POSTAG = '[/Prev]'
ADVERB_POSTAG = '[/Adv]'
ADVERBIAL_PRONOUN_POSTAG = '[/Adv|Pro]'
ADJECTIVE_POSTAG = '[/Adj]'
INFINITIVE_POSTAG = '[/V][Inf'  # nem hiányzik a végéről semmi!
ARTICLE_POSTAG = '[/Det|Art'
NOUN_POSTAG = '[/N]'
QUESTION_PARTICLE_POSTAG = '[/QPtcl]'
DET_PRO_POSTAG = '[/Det|Pro]'
N_PRO_POSTAG = '[/N|Pro'
MODAL_PARTICIPLE_MORPHEME = '[_ModPtcp/Adj]'
PERFECT_PARTICIPLE_MORPHEME = '[_PerfPtcp/Adj]'
IMPERFECT_PARTICIPLE_MORPHEME = '[_ImpfPtcp/Adj]'
ADVERBIAL_PARTICIPLE_MORPHEME = '[_AdvPtcp/Adv]'
FUTURE_PARTICIPLE_MORPHEME = '[_FutPtcp/Adj]'
GERUND_MORPHEME = '[_Ger/N]'
MANNER_MORPHEME = '[_Manner/Adv]'
SUPERLATIVE_MORPHEME = '[/Supl]'
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

            if ((central.xpostag.startswith((VERB_POSTAG, ADJECTIVE_POSTAG,
                                            SUPERLATIVE_MORPHEME)) and
                    PREVERB_POSTAG in central.anas and
                    contains_preverb(central))
                or (central.xpostag.startswith(NOUN_POSTAG) and
                    PREVERB_POSTAG in central.anas)):
                    self.add_preverb(central, 0)

            elif (central.xpostag.startswith(VERB_POSTAG)
                and is_eligible_preverb(left[4], 4)
                and left[3].lemma == "kell"
                and left[2].form == ","
                and left[1].form == "hogy"
                ):
                self.add_preverb(central, -4, left[4])

            elif (central.xpostag.startswith(VERB_POSTAG)
                and is_eligible_preverb(left[3], 3)
                and left[2].lemma == "kell"
                and left[1].form == "hogy"
                ):
                self.add_preverb(central, -3, left[3])

            elif (
                ((central.xpostag.startswith(ADJECTIVE_POSTAG)
                    and MANNER_MORPHEME not in central.xpostag
                    and (PERFECT_PARTICIPLE_MORPHEME in central.anas
                         or IMPERFECT_PARTICIPLE_MORPHEME in central.anas
                         or FUTURE_PARTICIPLE_MORPHEME in central.anas))
                or
                (central.xpostag.startswith((NOUN_POSTAG,ADJECTIVE_POSTAG))
                    and GERUND_MORPHEME in central.anas))
                and is_eligible_preverb(left[2], 2)
                and left[1].form in ('nem', 'sem', 'se', 'is')):
                    # Kalivoda (2021: 69-73)
                self.add_preverb(central, -2, left[2])

            elif (central.xpostag.startswith(VERB_POSTAG)
                and (ADVERBIAL_PARTICIPLE_MORPHEME in central.anas
                    or central.xpostag.startswith(INFINITIVE_POSTAG))
                and is_eligible_preverb(left[3], 3)
                and left[2].xpostag.startswith((ADVERB_POSTAG,
                                ADVERBIAL_PRONOUN_POSTAG, VERB_POSTAG,
                                ARTICLE_POSTAG))
                and (left[1].xpostag.startswith((ADVERB_POSTAG,
                                ADVERBIAL_PRONOUN_POSTAG, VERB_POSTAG))
                     or left[1].form in CONTRAST_PARTICLES
                     or left[1].xpostag.startswith((DET_PRO_POSTAG,
                                N_PRO_POSTAG, QUESTION_PARTICLE_POSTAG,
                                ARTICLE_POSTAG)))
                ):
                self.add_preverb(central, -3, left[3])

            elif (central.xpostag.startswith(VERB_POSTAG)
                and (ADVERBIAL_PARTICIPLE_MORPHEME in central.anas
                    or central.xpostag.startswith(INFINITIVE_POSTAG))
                and is_eligible_preverb(left[2], 2)
                and (left[1].xpostag.startswith((ADVERB_POSTAG,
                                ADVERBIAL_PRONOUN_POSTAG, VERB_POSTAG)))
                and not right[1].xpostag.startswith(INFINITIVE_POSTAG)
                ):
                self.add_preverb(central, -2, left[2])

            elif (
                (central.xpostag.startswith(VERB_POSTAG)
                    and VERB_POSTAG in central.anas  # is it a verb according to anas?
                    and central.form != "volna"
                    and central.lemma != "kell"
                    and not (right[1].xpostag.startswith(INFINITIVE_POSTAG)
                             and not contains_preverb(right[1])
                             or right[2].xpostag.startswith(INFINITIVE_POSTAG)))
                    and not (central.lemma in ("van", "lesz")
                             and (ADVERBIAL_PARTICIPLE_MORPHEME in right[1].xpostag
                                  or ADVERBIAL_PARTICIPLE_MORPHEME in right[2].xpostag)
                             )
                or
                (central.xpostag.startswith(ADJECTIVE_POSTAG)
                    and (MODAL_PARTICIPLE_MORPHEME in central.anas
                         or FUTURE_PARTICIPLE_MORPHEME in central.anas) # Kalivoda (2021: 68-9)
                    and MANNER_MORPHEME not in central.xpostag
                    and PREVERB_POSTAG not in central.anas)
                or
                (central.xpostag == ADVERB_POSTAG
                    and ADVERBIAL_PARTICIPLE_MORPHEME in central.anas)   # Kalivoda (2021: 64-6)
                ):

                # Case 2: "szét" [msd="IGE.*|HA.*"] [msd="IGE.*" & word != "volna"]
                # szét kell szerelni, szét se szereli
                if (is_eligible_preverb(left[2], 2) and
                      left[1].xpostag.startswith((ADVERB_POSTAG,
                                    ADVERBIAL_PRONOUN_POSTAG, VERB_POSTAG))):
                    self.add_preverb(central, -2, left[2])

                # Case 3: [msd="IGE.*" & word != "volna] "szét"
                elif is_eligible_preverb(right[1]):
                    self.add_preverb(central, 1, right[1])

                # Case 4: [msd="IGE.*" & word != "volna] [msd="HA.*" | word="volna"] "szét"
                # rágja is szét, rágta volna szét, tépi hirtelen szét
                elif (is_eligible_preverb(right[2]) and
                        (right[1].xpostag.startswith((ADVERB_POSTAG,
                                            ADVERBIAL_PRONOUN_POSTAG))
                         or right[1].xpostag == QUESTION_PARTICLE_POSTAG
                         or right[1].form == 'volna'
                         or right[1].form in CONTRAST_PARTICLES
                         or right[1].xpostag.startswith((NOUN_POSTAG,
                                            DET_PRO_POSTAG, N_PRO_POSTAG))
                         )
                      ):
                    self.add_preverb(central, 2, right[2])

                elif (is_eligible_preverb(right[3])
                    and right[1].xpostag.startswith((ADVERB_POSTAG,
                                    ADVERBIAL_PRONOUN_POSTAG,
                                    N_PRO_POSTAG, NOUN_POSTAG, DET_PRO_POSTAG,
                                    ARTICLE_POSTAG))
                    and right[2].xpostag.startswith((ADVERB_POSTAG,
                                    ADVERBIAL_PRONOUN_POSTAG,
                                    N_PRO_POSTAG, NOUN_POSTAG, DET_PRO_POSTAG))
                    ):
                    self.add_preverb(central, 3, right[3])

                elif (is_eligible_preverb(left[1])
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

            # needs to be collected and postprocessed before printing
            processed.append(central)

        # Clean up processed:
        # Remove "sep" annotation from verbs that are "orphaned" because
        # a better main verb candidate was found for the preverb later in
        # the sentence.
        # Set verb and preverb lemmas.

        conn_id_to_lemma = {proc_word.previd: proc_word.lemma
                            for proc_word in processed
                            if proc_word.prev == "conn"}

        for proc_word in processed:
            if proc_word.prev == "conn": # word is a preverb
                proc_word.lemma = ""
                proc_word.prevpos = ""
            elif proc_word.prev == "sep": # word is verb
                if proc_word.previd in conn_id_to_lemma:
                    # verb is not orphaned
                    vlemma = proc_word.lemma.lower()
                    proc_word.lemma = conn_id_to_lemma[proc_word.previd]\
                                      + vlemma
                    if self.compound_exists:
                        proc_word.compound = conn_id_to_lemma[proc_word.previd]\
                                             + '#' + vlemma
                else:
                    # verb is orphaned
                    proc_word.prev = ""
                    proc_word.previd = ""
                    proc_word.prevpos = ""


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
            self.prev_id += 1
            previd = str(self.prev_id)

            # handle verb  --> moved to postprocessing
#            vlemma = verb.lemma.lower()
#            verb.lemma = preverb.lemma + vlemma
#            if self.compound_exists:
#                verb.compound = preverb.lemma + '#' + vlemma
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

##           moved to postprocessing:
#            preverb.lemma = ''

#            if self.compound_exists:
#                preverb.compound = preverb.lemma       # ?
            preverb.prev = 'conn'
            preverb.previd = previd
            verb.prevpos = "{:+0}".format(prevpos)
            preverb.prevpos = str(prevpos)
        else:
            verb.prev = 'pfx'

def contains_preverb(verb):
    """
    Check whether the verb form contains a preverb according to
    the analysis selected by the pos tagger.
    """
    anas_list = json.loads(verb.anas)
    last_good_ana = None
    for ana in anas_list:
        if ana["lemma"] == verb.lemma and ana["tag"] == verb.xpostag:
            last_good_ana = ana
    if last_good_ana is None:
        return False
    else:
        return PREVERB_POSTAG in last_good_ana.get('readable')

def is_eligible_preverb(word, distance=0):
    """
    Check whether the word is annotated as preverb and whether
    it has already been connected to a verb that is closer to it.
    """
    return (
        word.xpostag == PREVERB_POSTAG
        and (word.prev != "conn" or int(word.prevpos) >= distance)
    )
