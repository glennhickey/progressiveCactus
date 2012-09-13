modules = submodules

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