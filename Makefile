
virtPyDir = $(CURDIR)/python
virtPyEnv = ${virtPyDir}/bin/activate
virtPy = ${virtPyDir}/bin/python
export

.PHONY: all clean test ucsc ucscClean 

all : 
	cd submodules && make all

clean:
	cd submodules && make clean

test:
	cd submodules && make test

ucsc:
	cd submodules && make justUCSC

ucscClean:
	cd submodules && make justUCSCClean
