include include.mk

external = tokyocabinet kyotocabinet kyototycoon lastz hdf5
ucsc = sonLib jobTree pinchesAndCacti matchingAndOrdering cactus hal cactus2hal mafJoin

modules = ${external} ${ucsc}
#modules = ${ucsc}

.PHONY: all %.all clean %.clean envRereshRule virtPyRule lastzRule tokyocabinetRule kyotocabinetRule hdf5Rule lastzClean cabinetClean hdf5Clean test %.test datasets

all : envRefreshRule virtPyRule lastzRule tokyocabinetRule kyotocabinetRule kyototycoonRule hdf5Rule datasets ${ucsc:%=ucsc.%}

envRefreshRule:
	rm -f ${myEnv}

virtPyRule :
	python $(CURDIR)/virtualenv/virtualenv.py ${virtPyDir}
	source ${virtPyEnv} && cd $(CURDIR)/networkx && ${virtPy} setup.py install
	source ${virtPyEnv} && cd $(CURDIR)/psutil/ && ${virtPy} setup.py install
	cp ${virtPyEnv} ${myEnv}
	echo PYTHONPATH=$(CURDIR):\$$PYTHONPATH >> ${myEnv}
	echo PATH=${virtPyDir}/bin:\$$PATH >> ${myEnv}

lastzRule :
	cd lastz && make
	echo PATH=$(CURDIR)/lastz/src:$(CURDIR)/lastz/tools:\$$PATH >> ${myEnv}

tokyocabinetRule :
	cd tokyocabinet &&./configure --prefix=$(CURDIR)/tokyocabinet && make && make install
	echo PATH=$(CURDIR)/tokyocabinet/bin:\$$PATH >> ${myEnv}

kyotocabinetRule :
	cd kyotocabinet &&./configure --prefix=$(CURDIR)/kyotocabinet && make && make install
	echo PATH=$(CURDIR)/kyotocabinet/bin:\$$PATH >> ${myEnv}

kyototycoonRule :
	cd kyototycoon &&./configure --prefix=$(CURDIR)/kyototycoon --with-kc=$(CURDIR)/kyotocabinet && make && make install
	echo PATH=$(CURDIR)/kyototycoon/bin:\$$PATH >> ${myEnv}

hdf5Rule :
	cd hdf5 &&./configure --prefix=$(CURDIR)/hdf5 --enable-cxx && make && make install
	echo PATH=$(CURDIR)/hdf5/bin:\$$PATH >> ${myEnv}

# Important to export environment to override sonlib/include.mk
export

ucsc.%:
	cd $* && make
	echo PATH=$(CURDIR)/$*/bin:\$$PATH >> ${myEnv}

clean: lastzClean cabinetClean hdf5Clean ${ucsc:%=clean.%}

clean.%:
	cd $* && make clean

lastzClean:
	cd lastz && make clean

cabinetClean:
	rm -f $(CURDIR)/tokyocabinet/lib/*.a $(CURDIR)/kyotocabinet/lib/*.a  $(CURDIR)/kyototycoon/lib/*.a

hdf5Clean:
	cd hdf5 && make clean

test: ${ucsc:%=test.%}

test.%:
	source ${myEnv} && cd $* && make test

datasets:
	echo SON_TRACE_DATASETS=$(CURDIR)/cactusTestData >> ${myEnv}
