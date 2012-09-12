# order is important, libraries first
external = tokyocabinet kyototycoon lastz hdf5
ucsc = sonLib jobTree pinchesAndCacti matchingAndOrdering cactus hal cactus2hal mafTools

#modules = ${external} ${ucsc}
modules = ${ucsc}

.PHONY: all %.all clean %.clean

all : lastzRule tokyocabinetRule kyototycoonRule ${ucsc:%=all.%}

all.%:
	cd $* && make

lastzRule :
	cd lastz && make

tokyocabinetRule :
	cd tokyocabinet &&./configure --prefix=$(CURDIR)/tokyocabinet && make && make install

kyototycoonRule :
	cd kyototycoon &&./configure --prefix=$(CURDIR)/kyototycoon --with-kc=$(CURDIR)/tokyocabinet && make && make install


clean: lastzClean ${modules:%=clean.%}

clean.%:
	cd $* && make clean

lastzClean:
	cd lastz && make clean

test: all
	python allTests.py