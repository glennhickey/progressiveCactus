include include.mk

externalModules = zlib tokyocabinet kyotocabinet kyototycoon lastz hdf5 pbs-drmaa
ucscModules = sonLib jobTree pinchesAndCacti matchingAndOrdering cactus hal cactus2hal

modules = ${externalModules} ${ucscModules}
#modules = ${ucsc}

.PHONY: all %.all justUCSC %.justUCSC envRefreshRule virtPyRule pbsDrmaaRule drmaaPythonRule lastzRule zlibRule tokyocabinetRule kyotocabinetRule kyototycoonRule hdf5Rule %.ucsc clean %.clean justUCSCClean %.justUCSCClean zlibClean lastzClean cabinetClean pbsDrmaaClean hdf5Clean test %.test datasets

all : envRefreshRule virtPyRule lastzRule zlibRule tokyocabinetRule kyotocabinetRule kyototycoonRule pbsDrmaaRule drmaaPythonRule hdf5Rule datasets ${ucscModules:%=ucsc.%}

justUCSC : ${ucscModules:%=ucsc.%}

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

tokyocabinetRule :
	cd tokyocabinet &&./configure --prefix=$(CURDIR)/tokyocabinet ${ktlinkingflags} --disable-bzip && make && make install
	echo export PATH=$(CURDIR)/tokyocabinet/bin:\$$PATH >> ${myEnv}

kyotocabinetRule :
	cd kyotocabinet &&./configure --prefix=$(CURDIR)/kyotocabinet ${ktlinkingflags} && make && make install
	echo export PATH=$(CURDIR)/kyotocabinet/bin:\$$PATH >> ${myEnv}

kyototycoonRule :
	cd kyototycoon &&./configure --prefix=$(CURDIR)/kyototycoon ${ktlinkingflags} --with-kc=$(CURDIR)/kyotocabinet && make && make install
	echo export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) >> ${myEnv}
	echo export PATH=$(CURDIR)/kyototycoon/bin:\$$PATH >> ${myEnv}

hdf5Rule :
	cd hdf5 &&./configure --prefix=$(CURDIR)/hdf5 --enable-cxx && make && make install
	echo export PATH=$(CURDIR)/hdf5/bin:\$$PATH >> ${myEnv}


# Important to export environment to override sonlib/include.mk
export

ucsc.%:
	cd $* && make
	echo export PATH=$(CURDIR)/$*/bin:\$$PATH >> ${myEnv}

clean: lastzClean cabinetClean hdf5Clean pbsDrmaaClean zlibClean ${ucscModules:%=clean.%}

clean.%:
	cd $* && make clean

justUCSCClean: ${ucscModules:%=justUCSCClean.%}

justUCSCClean.%:
	cd $* && make clean

zlibClean:
	cd zlib && make clean

lastzClean:
	cd lastz && make clean

cabinetClean:
	cd kyotocabinet && make clean
	cd kyototycoon && make clean
	rm -f $(CURDIR)/tokyocabinet/lib/*.a $(CURDIR)/kyotocabinet/lib/*.a  $(CURDIR)/kyototycoon/lib/*.a

ifeq ($(enablePBSTorque), yes)
pbsDrmaaClean:
	cd pbs-drmaa && make clean
else
pbsDrmaaClean:
	cd .
endif

hdf5Clean:
	cd hdf5 && make clean

test: ${ucscModules:%=test.%}

test.%:
	. ${myEnv} && cd $* && make test

datasets:
	echo export SON_TRACE_DATASETS=$(CURDIR)/cactusTestData >> ${myEnv}
