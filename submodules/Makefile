include include.mk

externalModules = zlib tokyocabinet kyotocabinet kyototycoon hdf5 pbs-drmaa clapack phast kentToolBinaries
ucscModules = sonLib jobTree pinchesAndCacti matchingAndOrdering cactus hal cactus2hal

modules = ${externalModules} ${ucscModules}
#modules = ${ucsc}

.PHONY: all %.all justUCSC %.justUCSC envRefreshRule virtPyRule pbsDrmaaRule drmaaPythonRule zlibRule tokyocabinetRule kyotocabinetRule kyototycoonRule hdf5Rule clapackRule phastRule kentToolBinariesRule %.ucsc clean %.clean justUCSCClean %.justUCSCClean zlibClean cabinetClean pbsDrmaaClean hdf5Clean clapckClean phastClean kentToolBinariesClean test %.test datasets

all : envRefreshRule virtPyRule zlibRule tokyocabinetRule kyotocabinetRule kyototycoonRule pbsDrmaaRule drmaaPythonRule clapackRule phastRule kentToolBinariesRule hdf5Rule datasets ${ucscModules:%=ucsc.%}

justUCSC : ${ucscModules:%=ucsc.%}

envRefreshRule:
	rm -f ${myEnv}

virtPyRule :
	python $(PWD)/virtualenv/virtualenv.py ${virtPyDir}
	. ${virtPyEnv} && cd $(PWD)/networkx && ${virtPy} setup.py install
	. ${virtPyEnv} && cd $(PWD)/psutil/ && ${virtPy} setup.py install
	. ${virtPyEnv} && cd $(PWD)/biopython/ && echo y | ${virtPy} setup.py install | cat
	cp ${virtPyEnv} ${myEnv}
	echo export PYTHONPATH=$(PWD):\$$PYTHONPATH >> ${myEnv}
	echo export PATH=${virtPyDir}/bin:\$$PATH >> ${myEnv}

ifeq ($(enablePBSTorque), yes)
pbsDrmaaRule :
	cd pbs-drmaa &&./configure --prefix=$(PWD)/pbs-drmaa && make && make install
	echo export DRMAA_LIBRARY_PATH=$(PWD)/pbs-drmaa/lib/libdrmaa.so >> ${myEnv}

drmaaPythonRule :
	. ${virtPyEnv} && cd $(PWD)/drmaa-python/ && ${virtPy} setup.py install
else
pbsDrmaaRule :
	cd .

drmaaPythonRule :
	cd . 
endif

zlibRule :
	cd zlib && ./configure --prefix=$(PWD)/zlib && make && make install
	echo export PATH=$(PWD)/zlib/bin:\$$PATH >> ${myEnv}

tokyocabinetRule :
	cd tokyocabinet &&./configure --prefix=$(PWD)/tokyocabinet ${ktlinkingflags} --disable-bzip && make && make install
	echo export PATH=$(PWD)/tokyocabinet/bin:\$$PATH >> ${myEnv}
	echo export tokyoCabinetIncl=\"-I$(PWD)/tokyocabinet/include -DHAVE_TOKYO_CABINET=1\" >> ${myEnv}
	echo export tokyoCabinetLib=\"-L$(PWD)/tokyocabinet/lib -Wl,-rpath,$(PWD)/tokyocabinet/lib -ltokyocabinet -lz -lbz2 -lpthread -lm\" >> ${myEnv}

kyotocabinetRule :
	cd kyotocabinet &&./configure --prefix=$(PWD)/kyotocabinet ${ktlinkingflags} && make && make install
	echo export PATH=$(PWD)/kyotocabinet/bin:\$$PATH >> ${myEnv}

kyototycoonRule :
	cd kyototycoon &&./configure --prefix=$(PWD)/kyototycoon ${ktlinkingflags} --with-kc=$(PWD)/kyotocabinet && make && make install
	echo export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) >> ${myEnv}
	echo export PATH=$(PWD)/kyototycoon/bin:\$$PATH >> ${myEnv}
	echo export kyotoTycoonIncl=\"-I$(PWD)/kyotocabinet/include -I$(PWD)/kyototycoon/include -DHAVE_KYOTO_TYCOON=1\" >> ${myEnv}
	echo export kyotoTycoonLib=\"-L$(PWD)/kyototycoon/lib -L$(PWD)/kyotocabinet/lib -Wl,-rpath,$(PWD)/kyototycoon/lib -lkyototycoon -lkyotocabinet -lz -lbz2 -lpthread -lm -lstdc++\" >> ${myEnv}

ifneq ($(TARGETOS), Darwin)
CLAPACKPHASTFLAGS = CLAPACKPATH=$(PWD)/clapack
clapackRule :
	cd clapack && make f2clib && make blaslib && make lib
else
CLAPACKPHASTFLAGS = 
clapackRule :
	cd .
endif

ifdef ENABLE_PHYLOP
phastRule :
	cd phast/src && make $(CLAPACKPHASTFLAGS)
	echo export PATH=$(PWD)/phast/bin:\$$PATH >> ${myEnv}
else
phastRule :
	cd .
endif

kentToolBinariesRule :
	cd kentToolBinaries && make
	echo export PATH=$(PWD)/kentToolBinaries:\$$PATH >> ${myEnv}

hdf5Rule :
	cd hdf5 &&./configure --prefix=$(PWD)/hdf5 --enable-cxx && make && make install
	echo export PATH=$(PWD)/hdf5/bin:\$$PATH >> ${myEnv}


# Important to export environment to override sonlib/include.mk
export

ucsc.%:
	cd $* && make
	echo export PATH=$(PWD)/$*/bin:\$$PATH >> ${myEnv}

clean: cabinetClean hdf5Clean pbsDrmaaClean zlibClean clapackClean phastClean kentToolBinariesClean ${ucscModules:%=clean.%}

clean.%:
	cd $* && make clean

justUCSCClean: ${ucscModules:%=justUCSCClean.%}

justUCSCClean.%:
	cd $* && make clean

zlibClean:
	cd zlib && make clean

cabinetClean:
	cd kyotocabinet && make clean
	cd kyototycoon && make clean
	rm -f $(PWD)/tokyocabinet/lib/*.a $(PWD)/kyotocabinet/lib/*.a  $(PWD)/kyototycoon/lib/*.a

ifeq ($(enablePBSTorque), yes)
pbsDrmaaClean:
	cd pbs-drmaa && make clean
else
pbsDrmaaClean:
	cd .
endif

ifneq ($(TARGETOS), Darwin)
clapackClean :
	cd clapack && make clean
else
clapackClean :
	cd .
endif

ifdef ENABLE_PHYLOP
phastClean :
	cd phast/src && make clean
else
phastClean :
	cd .
endif

kentToolBinariesClean :
	cd kentToolBinaries && make clean

hdf5Clean:
	cd hdf5 && make clean

test: ${ucscModules:%=test.%}

test.%:
	. ${myEnv} && cd $* && make test

datasets:
	echo export SON_TRACE_DATASETS=$(PWD)/cactusTestData >> ${myEnv}
