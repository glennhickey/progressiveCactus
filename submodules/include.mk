#Modify this variable to set the location of sonLib
sonLibRootPath=$(CURDIR)/sonLib
sonLibPath=${sonLibRootPath}/lib


#OVERRIDE SONLIB WITH LOCAL DBS (because now sonlib won't redefine if exist)
tcPrefix = $(CURDIR)/tokyocabinet
tokyoCabinetIncl = -I ${tcPrefix}/include -DHAVE_TOKYO_CABINET=1
tokyoCabinetLib = -L${tcPrefix}/lib -Wl,-rpath,${tcPrefix}/lib -ltokyocabinet -lz -lbz2 -lpthread -lm

kcPrefix =$(CURDIR)/kyotocabinet
ttPrefix =$(CURDIR)/kyototycoon
kyotoTycoonIncl = -I${kcPrefix}/include -I${ttPrefix}/include -DHAVE_KYOTO_TYCOON=1
kyotoTycoonLib = -L${ttPrefix}/lib -Wl,-rpath,${ttPrefix}/lib -lkyototycoon -L${kcPrefix}/lib -Wl,-rpath,${kcPrefix}/lib -lkyotocabinet -lz -lbz2 -lpthread -lm -lstdc++

include  ${sonLibRootPath}/include.mk

dataSetsPath=/Users/benedictpaten/Dropbox/Documents/work/myPapers/genomeCactusPaper/dataSets

cflags += -I ${sonLibPath} ${tokyoCabinetIncl} ${kyotoTycoonIncl} ${mysqlIncl} ${pgsqlIncl}
basicLibs = ${sonLibPath}/sonLib.a ${sonLibPath}/cuTest.a ${dblibs}
basicLibsDependencies = ${sonLibPath}/sonLib.a ${sonLibPath}/cuTest.a 

#put hdf5 at beginning of path
h5path = $(CURDIR)/hdf5
PATH := ${h5path}/bin:${PATH}
h5prefix = -prefix=${h5path}

#environment
myEnv = $(CURDIR)/../environment
