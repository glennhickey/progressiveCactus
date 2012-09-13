modules = submodules

.PHONY: all %.all clean %.clean

all : ${modules:%=all.%}

all.%:
	echo ${kyotoTycoonIncl}
	cd $* && make all 

clean:  ${modules:%=clean.%}
	cd $* && make clean

clean.%:
	cd $* && make clean

test: all
	python allTests.py