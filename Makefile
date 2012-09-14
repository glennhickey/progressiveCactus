modules = submodules

virtPyDir = $(CURDIR)/python
virtPyEnv = ${virtPyDir}/bin/activate
virtPy = ${virtPyDir}/bin/python
export

.PHONY: all %.all clean %.clean

all : ${modules:%=all.%}

all.%:
	cd $* && make all 

clean:  ${modules:%=clean.%}
	cd $* && make clean

clean.%:
	cd $* && make clean

test: all
	python allTests.py