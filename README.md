# emPreverb

An emtsv module to __connect a preverb to its verb__ or verb-derivative
token to which it belong. To be used for Hungarian.

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
