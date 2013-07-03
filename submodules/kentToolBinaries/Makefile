kentBinDeps = wigToBigWig faToTwoBit bedToBigBed 

ifeq ($(TARGETOS), Darwin)
urlSubDirectory = macOSX.x86_64
else
urlSubDirectory = linux.x86_64
endif

.PHONY: all %.all kentBinDeps %.kentBinDeps clean %.clean 

all : ${kentBinDeps:%=kent.%}

clean : ${kentBinDeps:%=kentClean.%}

kent.% :
	test -s $* || wget "http://hgdownload.cse.ucsc.edu/admin/exe/${urlSubDirectory}/$*" && chmod u+x $*

kentClean.% :
	rm -f $*
