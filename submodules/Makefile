include include.mk

external = tokyocabinet kyotocabinet kyototycoon lastz hdf5
ucsc = sonLib jobTree pinchesAndCacti matchingAndOrdering cactus hal cactus2hal mafTools

modules = ${external} ${ucsc}
#modules = ${ucsc}

.PHONY: all %.all clean %.clean lastzRule tokyocabinetRule kyotocabinetRule hdf5Rule lastzClean cabinetClean hdf5Clean test

all : lastzRule tokyocabinetRule kyotocabinetRule kyototycoonRule hdf5Rule ${ucsc:%=ucsc.%}

lastzRule :
	cd lastz && make

tokyocabinetRule :
	cd tokyocabinet &&./configure --prefix=$(CURDIR)/tokyocabinet && make && make install

kyotocabinetRule :
	cd kyotocabinet &&./configure --prefix=$(CURDIR)/kyotocabinet && make && make install

kyototycoonRule :
	cd kyototycoon &&./configure --prefix=$(CURDIR)/kyototycoon --with-kc=$(CURDIR)/kyotocabinet && make && make install

hdf5Rule :
	cd hdf5 &&./configure --prefix=$(CURDIR)/hdf5 --enable-cxx && make && make install

# Important to export environment to override sonlib/include.mk
export

ucsc.%:
	cd $* && make

clean: lastzClean cabinetClean hdf5Clean ${modules:%=clean.%}

clean.%:
	cd $* && make clean

lastzClean:
	cd lastz && make clean

cabinetClean:
	rm -f $(CURDIR)/tokyocabinet/lib/*.a $(CURDIR)/kyotocabinet/lib/*.a  $(CURDIR)/kyototycoon/lib/*.a

hdf5Clean:
	cd hdf5 && make clean


test: all
	python allTests.py