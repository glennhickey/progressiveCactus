# order is important, libraries first
external = tokyocabinet kyototycoon lastz hdf5
ucsc = sonLib jobTree pinchesAndCacti matchingAndOrdering cactus hal cactus2hal mafTools
#modules = ${external} ${ucsc}
modules = ${ucsc}

.PHONY: all %.all clean %.clean

all : ${modules:%=all.%}

all.%:
	cd $* && make

clean:  ${modules:%=clean.%}
	cd $* && make clean

clean.%:
	cd $* && make clean

test: all
	python allTests.py