# emDummy
A template module for xtsv

Take a look at this toy module for getting started
writing an [`xtsv`](https://github.com/nytud/xtsv) module.

This module is for educational purposes.
It solves an extremely simple task:
 * takes the value of the `form` field;
 * create a new field called `star` which will contain the value of the `form` field together with an added asterisk on both sides.

E.g. if the `form` field is `kutya` the `star` field will be `*kutya*`.

It is demonstrated that the order of the columns does _not_ affect the operation of `xtsv`.

For a bit more advanced example see: [`emdummy`](https://github.com/nytud/emdummy).

## Python package creation

By executing

```bash
make
```

1. a virtual environment is created in `venv`;
2. `emdummy` Python package is created
in `dist/emdummy-*-py3-none-any.whl`;
3. the package is installed in `venv`;
4. the package is tested (see __testing__).

The Python package can be installed anywhere by direct path:

```bash
pip install ./dist/emPreverb-*-py3-none-any.whl
```

## Testing

After the Python package is ready:

```bash
make test
```

runs `emdummy` on `data/test*.tsv`
and compares the output with `out/test*.tsv`.

