include include.mk

external = zlib bzip2 tokyocabinet kyotocabinet kyototycoon lastz hdf5 pbs-drmaa
ucsc = sonLib jobTree pinchesAndCacti matchingAndOrdering cactus hal cactus2hal mafJoin

modules = ${external} ${ucsc}
#modules = ${ucsc}

.PHONY: all %.all clean %.clean envRereshRule virtPyRule lastzRule zlibRule bzip2Rule tokyocabinetRule kyotocabinetRule pbsDrmaaRule drmaaPythonRule hdf5Rule zlibClean bzip2Clean lastzClean cabinetClean hdf5Clean pbsDrmaaClean test %.test datasets

all : envRefreshRule virtPyRule lastzRule zlibRule bzip2Rule tokyocabinetRule kyotocabinetRule kyototycoonRule pbsDrmaaRule drmaaPythonRule hdf5Rule datasets ${ucsc:%=ucsc.%}

justUCSC : ${ucsc:%=ucsc.%}

envRefreshRule:
	rm -f ${myEnv}

virtPyRule :
	python $(CURDIR)/virtualenv/virtualenv.py ${virtPyDir}
	. ${virtPyEnv} && cd $(CURDIR)/networkx && ${virtPy} setup.py install
	. ${virtPyEnv} && cd $(CURDIR)/psutil/ && ${virtPy} setup.py install
	cp ${virtPyEnv} ${myEnv}
	echo export PYTHONPATH=$(CURDIR):\$$PYTHONPATH >> ${myEnv}
	echo export PATH=${virtPyDir}/bin:\$$PATH >> ${myEnv}

ifeq ($(enablePBSTorque), yes)
pbsDrmaaRule :
	cd pbs-drmaa &&./configure --prefix=$(CURDIR)/pbs-drmaa && make && make install
	echo export DRMAA_LIBRARY_PATH=$(CURDIR)/pbs-drmaa/lib/libdrmaa.so >> ${myEnv}

drmaaPythonRule :
	. ${virtPyEnv} && cd $(CURDIR)/drmaa-python/ && ${virtPy} setup.py install
else
pbsDrmaaRule :
	cd .

drmaaPythonRule :
	cd . 
endif

lastzRule :
	cd lastz && make
	echo export PATH=$(CURDIR)/lastz/src:$(CURDIR)/lastz/tools:\$$PATH >> ${myEnv}

zlibRule :
	cd zlib && ./configure --prefix=$(CURDIR)/zlib && make && make install
	echo export PATH=$(CURDIR)/zlib/bin:\$$PATH >> ${myEnv}

bzip2Rule :
	cd bzip2 && make && make install PREFIX=$(CURDIR)/bzip2
	cd bzip2 && make clean && make -f Makefile-libbz2_so PREFIX=$(CURDIR)/bzip2
	echo export PATH=$(CURDIR)/bzip2/bin:\$$PATH >> ${myEnv}

tokyocabinetRule :
	cd tokyocabinet &&./configure --prefix=$(CURDIR)/tokyocabinet ${ktlinkingflags} && make && make install
	echo export PATH=$(CURDIR)/tokyocabinet/bin:\$$PATH >> ${myEnv}

kyotocabinetRule :
	cd kyotocabinet &&./configure --prefix=$(CURDIR)/kyotocabinet ${ktlinkingflags} && make && make install
	echo export PATH=$(CURDIR)/kyotocabinet/bin:\$$PATH >> ${myEnv}

kyototycoonRule :
	cd kyototycoon &&./configure --prefix=$(CURDIR)/kyototycoon ${ktlinkingflags} --with-kc=$(CURDIR)/kyotocabinet && make && make install
	echo export PATH=$(CURDIR)/kyototycoon/bin:\$$PATH >> ${myEnv}

hdf5Rule :
	cd hdf5 &&./configure --prefix=$(CURDIR)/hdf5 --enable-cxx && make && make install
	echo export PATH=$(CURDIR)/hdf5/bin:\$$PATH >> ${myEnv}


# Important to export environment to override sonlib/include.mk
export

ucsc.%:
	cd $* && make
	echo export PATH=$(CURDIR)/$*/bin:\$$PATH >> ${myEnv}

clean: lastzClean cabinetClean hdf5Clean pbsDrmaaClean ${ucsc:%=clean.%}

clean.%:
	cd $* && make clean

justUCSCClean: ${ucsc:%=justUCSCClean.%}

justUCSCClean.%:
	cd $* && make clean

zlibClean:
	cd zlib && make clean

bzip2Clean:
	cd bzip2 && make clean && make -f Makefile-libbz2_so clean

lastzClean:
	cd lastz && make clean

cabinetClean:
	rm -f $(CURDIR)/tokyocabinet/lib/*.a $(CURDIR)/kyotocabinet/lib/*.a  $(CURDIR)/kyototycoon/lib/*.a

pbsDrmaaClean:
	cd pbs-drmaa && make clean

hdf5Clean:
	cd hdf5 && make clean

test: ${ucsc:%=test.%}

test.%:
	. ${myEnv} && cd $* && make test

datasets:
	echo export SON_TRACE_DATASETS=$(CURDIR)/cactusTestData >> ${myEnv}
