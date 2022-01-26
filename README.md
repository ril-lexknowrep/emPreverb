# emPreverb

An emtsv module to __connect a preverb to its verb__ or verb-derivative
token to which it belongs. To be used for Hungarian.

See also: https://github.com/ril-lexknowrep/hungarian-preverb-corpus

## User's guide

### General features

This module is a rule-based tool that essentially uses a hand-crafted decision tree to connect Hungarian preverbs to their verbs from which they are separated in certain syntactic contexts. It uses information from emtsv's tok, morph and pos modules to decide whether a separated preverb should be connected to a particular verb. It connects preverbs only based on morphological and part of speech tags and surface word order cues, and thus it does not need either a lexicon which lists legitimate preverb-verb combinations, nor the output of a syntactic parser to work. Separated preverbs are not only connected to finite verb forms, but also to infinitives, adjectival and adverbial participles, and nomina actionis that are derived from verbs that have preverbs. A Hungarian preverb may be separated from the verb root in all of these words in certain syntactic contexts.

### Output

This module uses the following tsv output fields. The philosophy that underlies these annotations is explained in our emPreverb paper.

- **The `prev` field:** Verbs (by which we mean finite as well as non-finite verb forms and potentially separable verb derivatives) and preverbs are annotated as follows:
   - `pfx` marks a verb token that contains a prefixed, i.e. non-separated preverb.
   - `sep` marks a verb token from which a preverb was separated, i.e. a verb token to which a preverb token in the sentence belongs.
   - `conn` marks a separated preverb token which has been identified as belonging to a verb token in the sentence.

   The `sep` and `conn` annotations thus mark connected verb-preverb pairs. Verbs for which no corresponding preverb was found and preverbs to which no verb could be assigned by emPreverb are not annotated in any way, i.e. this field remains empty for them.
- **The `previd` field:** This field contains an unambiguous numerical identifier that indicates which `sep` verb a specific `conn` preverb belongs to. The preverb has the same `previd` value as the corresponding verb. `emPreverb` is only designed to handle one-to-one correspondences between separated preverbs and verbs, and thus coordinative structures in which arguably more than one preverb should be connected to a single verb, or vice versa, are not annotated as such (e.g. _meg kell és meg is lehet oldani; az öregje addig senkinek cipőt, csizmát nem szab a lábára, amíg meg nem nézette, szagoltatta, tapintatta velük a bőröket, hogy melyik lenne igazán a kedvükre való_).
- **The `prevpos` field:** This indicates the direction and distance of the separated preverb relative to its verb. This information only appears on verbs with separated preverbs, not on the preverbs, nor on verbs with a non-separated preverb. The value of `prevpos` consists of a number, which specifies the distance in tokens, and a sign, which specifies the direction. Minus means 'to the left' and plus means 'to the right'. For example, a value of `+1` would mean that the separated preverb is located immediately to the right of its verb, and `-2` indicates that the preverb is two tokens to the left of the verb, i.e. with one other token in between.
- **The `xpostag` field:** Although this is one of the required source fields of emPreverb, its value is also modified by it. For verbs with either a separated (`prev = "sep"`) or a non-separated preverb (`prev = "pfx"`), the label `[/Prev]` is prepended to the original value of `xpostag`. For example: _szétvetve_ becomes `[/Prev][/V][_AdvPtcp/Adv]` instead of the original `[/V][_AdvPtcp/Adv]` that is assigned to the `xpostag` field by emtsv's PurePos tagger module. The `xpostag` of the separated verb _nyelje_ in _a föld nyelje el_ becomes `[/Prev][/V][Sbjv.Def.3Sg]`.
- **The `lemma` field:** This is also a required source field of emPreverb which is modified by it. For verbs with a non-separated preverb the lemma is left unchanged. For `sep` verbs, the separated preverb is prepended to the verb's lemma. The lemma of `conn` preverbs is set to an empty string. In the previous example, PurePos originally assigns the values `nyel` and `el` to the `lemma` field of _nyelje_ and _el_ respectively. EmPreverb changes these to `elnyel` and the empty string (i.e. no lemma at all) respectively.
- **The `compound` field:** This field is the target field of our [emCompound](https://github.com/ril-lexknowrep/emCompound/) module. It is not required by emPreverb, but if emPreverb's input does contain the `compound` field, then emPreverb modifies it, adding the compound structure _preverb + # + verb lemma_ as the value of this field for `sep` verbs. This means that the value of the `compound` field of the token _nyelje_ in the above example, which is originally empty (as this form is not itself a compound), becomes `el#nyel`. Verb tokens with non-separated preverbs, like _szétvetve_, are already analysed as compounds, i.e. `szét#vet` by emCompound, so these are not changed.

**Important note on the ordering of modules:** Since emPreverb modifies the values of the `lemma` and `xpostag` fields that are assigned by emtsv pos, it **we do not recommend** running emPreverb before any other emtsv modules that use these two fields as their source fields. Thus emPreverb should ideally toward the end of the pipeline. If it is being used, then emCompound should be run before emPreverb. EmFilter and emToReadable can be safely run after emPreverb. EmToReadable can in fact convert emPreverb's output annotation into a human-readable format. 


### Example outputs

| | V prev | V previd | V prevpos | V xpostag | V lemma | V compound | P prev | P previd | P lemma |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| _**átúsztam**_ | pfx |  |  | `[/Prev][/V][Pst.NDef.1Sg]` | átúszik | át#úszik | | | |
| _**végig** kell **vinni**_ | sep | 1 | -2 | `[/Prev][/V][Inf]` | végigvisz | végig#visz | conn | 1 | `""` |
| _nem **gondolom** -e **meg**_ | sep | 2 | +2  | `[/Prev][/V][Prs.Def.1Sg]` | meggondol | meg#gondol | conn | 2 | `""` |
| _90 napot **meg** nem **haladó**_ | sep | 3 | -2 | `[/Prev][/Adj][Nom]` | meghaladó | meg#haladó | conn | 3 | `""` |

### Usage examples

Depending on the current configuration of your system, you might have to add the path to the emPreverb module on your machine (i.e. the path to your clone of the emPreverb repository) to the `PYTHONPATH` environmental variable like this before executing the commands below, otherwise you might get a 'module not found' error from the Python interpreter:

```
export PYTHONPATH="${PYTHONPATH}:/path/to/emPreverb/"
```

(Replace the part "`/path/to/emPreverb/`" by the actual absolute path to emPreverb on your machine.) In addition, if you are also using emCompound, you might have to do the same for the emCompound directory as well.

EmPreverb can be executed as an individual Python module. The file 'input.txt' in this example is a raw text file:

```
cat input.txt | docker run -i --rm mtaril/emtsv tok,morph,pos > pos_output.tsv
cat pos_output.tsv | python3 -m emPreverb > prev_output.tsv
```

Optionally, if [emCompound](https://github.com/ril-lexknowrep/emCompound/) is executed before emPreverb in the processing pipeline, then emPreverb adjusts the content of the `compound` field as described above:

```
cat input.txt | docker run -i --rm mtaril/emtsv tok,morph,pos > pos_output.tsv
cat pos_output.tsv | python3 -m emCompound | python3 emPreverb > prev_output.tsv
```

Alternatively, emPreverb can be run within emtsv as part of a processing pipeline:
```
cat input.txt | docker run -i --rm mtaril/emtsv tok,morph,pos,preverb > prev_output.tsv
```
Or together with emCompound:
```
cat input.txt | docker run -i --rm mtaril/emtsv tok,morph,pos,compound,preverb > prev_output.tsv
```

## Testing by hand

`pip install -r requirements.txt`
`make connect_preverbs`: if `compound` is present\
`make connect_preverbs_withcompound`: if `compound` field is _not_ present

Uses code in `emPreverb` directory directly.

## Python package creation

Just type `make` to run all the following.

1. A virtual environment is created in `venv`.
2. `emPreverb` Python package is created in `dist/emPreverb-*-py3-none-any.whl`.
3. The package is installed in `venv`. 
4. The package is unit tested on `tests/inputs/*.in` and outputs are compared with `tests/outputs/*.out`.

The above steps can be performed by `make venv`, `make build`, `make install` and `make test` respectively.

The Python package can be installed anywhere by direct path:
```bash
pip install ./dist/emPreverb-*-py3-none-any.whl
```

## Python package release

1. Check `emPreverb/version.py`.
2. `make release-major` or `make release-minor` or `make release-patch`.\
   This will update the version number appropriately make a `git commit` with a new `git` TAG.
3. `make` to recreate the package with the new tag in `dist/emPreverb-TAG-py3-none-any.whl`.
4. Go to `https://github.com/THISUSER/emPreverb` and _"Create release from tag"_.
5. Add wheel file from `dist/emPreverb-TAG-py3-none-any.whl` manually to the release.

## Add the released package to `emtsv`

1. Install [`emtsv`](https://github.com/nytud/emtsv/blob/master/docs/installation.md): 1st and 2nd point + `cython` only.
2. Go to the `emtsv` directory (`cd emtsv`).
1. Add `emPreverb` by adding this line to `requirements.txt`:\
   `https://github.com/THISUSER/emPreverb/releases/download/vTAG/emPreverb-TAG-py3-none-any.whl`
2. Complete `config.py` by adding `em_preverb` and `tools` from `emPreverb/__main__.py` appropriately.
3. Complete `emtsv` installation by `make venv`.
4. `echo "A kutya ment volna el sétálni." | venv/bin/python3 ./main.py tok,morph,pos > old`
5. `echo "A kutya ment volna el sétálni." | venv/bin/python3 ./main.py tok,morph,pos,preverb > new`
6. See results by `diff old new`.
7. If everything is in order, create a PR for `emtsv`.

That's it! :)

## Remarks

Based on `postprocess-emtsv/scripts/connect_prev.py` and [`emDummy`](https://github.com/nytud/emdummy).\
TODO command line argument `-v`.
