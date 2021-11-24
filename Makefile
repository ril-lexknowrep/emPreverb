SHELL:=/bin/bash

all:
	@echo "choose explicit target = type 'make ' and press TAB"

S=preverb
I=data
O=out

MODULE=preverb

# ===== MAIN STUFF


FILE=11341_prev

INFILE=$I/$(FILE).tsv
OUTFILE=$O/$(FILE).preverb


# compound field is usually added by `compound` module
# and this module alters its value;
# here, for testing,
# we add compound field with dummy "?" value manually
connect_preverbs:
	cat $(INFILE) | sed "s/\(.\)$$/\1	?/;s/xpostag	?$$/xpostag	compound/" | python3 $(MODULE) > $(OUTFILE)

connect_preverbs_no_compound:
	cat $(INFILE) | python3 $(MODULE) > $(OUTFILE).no_compound
