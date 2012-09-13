include include.mk
export

external = tokyocabinet kyotocabinet kyototycoon lastz hdf5
ucsc = sonLib jobTree pinchesAndCacti matchingAndOrdering cactus hal cactus2hal mafTools

modules = ${external} ${ucsc}
#modules = ${ucsc}

.PHONY: all %.all clean %.clean lastzRule tokyocabinetRule kyotocabinetRule hdf5Rule lastzClean cabinetClean hdf5Clean test

#all : lastzRule tokyocabinetRule kyotocabinetRule kyototycoonRule hdf5Rule ${ucsc:%=all.%}

all : ${ucsc:%=all.%}
all.%:
	cd $* && make

lastzRule :
	cd lastz && make

tokyocabinetRule : $(CURDIR)/tokyocabinet/lib/libtokyocabinet.a
	cd tokyocabinet &&./configure --prefix=$(CURDIR)/tokyocabinet && make && make install

kyotocabinetRule : $(CURDIR)/kyotocabinet/lib/libkyotocabinet.a
	cd kyotocabinet &&./configure --prefix=$(CURDIR)/kyotocabinet && make && make install

kyototycoonRule : $(CURDIR)/kyototycoon/lib/libkyototycoon.a
	cd kyototycoon &&./configure --prefix=$(CURDIR)/kyototycoon --with-kc=$(CURDIR)/kyotocabinet && make && make install

hdf5Rule : $(CURDIR)/hdf5/lib/libhdf5.a
	cd hdf5 &&./configure --prefix=$(CURDIR)/hdf5 --enable-cxx && make && make install

clean: lastzClean cabinetClean hdf5Clean ${modules:%=clean.%}

clean.%:
	cd $* && make clean

lastzClean:
	cd lastz && make clean

cabinetClean:
	rm -f $(CURDIR)/tokyocabinet/lib/*.a $(CURDIR)/kyotocabinet/lib/*.a  $(CURDIR)/kyototycoon/lib/*.a
	touch $(CURDIR)/tokyocabinet/lib/libtokyocabinet.a $(CURDIR)/kyotocabinet/lib/libkyotocabinet.a $(CURDIR)/kyototycoon/lib/libkyototycoon.a

hdf5Clean:
	cd hdf5 && make clean


test: all
	python allTests.py