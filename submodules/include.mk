#Modify this variable to set the location of sonLib
sonLibRootPath=$(CURDIR)/sonLib
sonLibPath=${sonLibRootPath}/lib


#OVERRIDE SONLIB WITH LOCAL DBS (because now sonlib won't redefine if exist)
tcPrefix = $(CURDIR)/tokyocabinet
tokyoCabinetIncl = -I ${tcPrefix}/include -DHAVE_TOKYO_CABINET=1
tokyoCabinetLib = -L${tcPrefix}/lib -Wl,-rpath,${tcPrefix}/lib -ltokyocabinet -lz -lpthread -lm

kcPrefix =$(CURDIR)/kyotocabinet
ttPrefix =$(CURDIR)/kyototycoon
kyotoTycoonIncl = -I${kcPrefix}/include -I${ttPrefix}/include -DHAVE_KYOTO_TYCOON=1 -I$(CURDIR)/zlib/include 
kyotoTycoonLib = -L$(CURDIR)/zlib/lib -L${ttPrefix}/lib -Wl,-rpath,${ttPrefix}/lib -lkyototycoon -L${kcPrefix}/lib -Wl,-rpath,${kcPrefix}/lib -lkyotocabinet -Wl,-rpath,$(CURDIR)/zlib/lib -lz -lpthread -lm -lstdc++

#DISABLE MYSQUL
mysqlIncl = 
mysqlLibs = -lm

include  ${sonLibRootPath}/include.mk
# copy over form sonlib so modules work with mavericks (namely kyoto cabinet)
CXX=${cpp}

dataSetsPath=/Users/benedictpaten/Dropbox/Documents/work/myPapers/genomeCactusPaper/dataSets

cflags += -I ${sonLibPath} ${tokyoCabinetIncl} ${kyotoTycoonIncl} ${mysqlIncl} ${pgsqlIncl}
cppflags += -I ${sonLibPath} ${tokyoCabinetIncl} ${kyotoTycoonIncl} ${mysqlIncl} ${pgsqlIncl}
basicLibs = ${sonLibPath}/sonLib.a ${sonLibPath}/cuTest.a ${dblibs}
basicLibsDependencies = ${sonLibPath}/sonLib.a ${sonLibPath}/cuTest.a 

#put hdf5 at beginning of path
h5path = $(CURDIR)/hdf5
PATH := ${h5path}/bin:${PATH}
h5prefix = -prefix=${h5path}

#environment
myEnv = $(CURDIR)/../environment

#kyoto tycoon et al have problems with shared libraries on the cluster
#but shared libraries seem to be necessary to build on osx.
LDFLAGS := -L$(CURDIR)/zlib/lib -L$(CURDIR)/kyotocabinet/lib $(LDFLAGS)
CXXFLAGS := $(cppflags) $(CXXFLAGS)
LD_LIBRARY_PATH := $(CURDIR)/zlib/lib:$(CURDIR)/kyotocabinet/lib:$(CURDIR)/kyototycoon/lib:$(LD_LIBRARY_PATH)
#UNAME := $(shell uname)
#ifeq ($(UNAME), Darwin)
ktlinkingflags =
#else
#ktlinkingflags = --enable-static --disable-shared 
#endif


#toggle support for PBS Torque batch system by changing value of
#enablePBSTorque between no and yes
# Torque must be installed for cactus to build with this enabled

enablePBSTorque = no
#enablePBSTorque = yes

ifndef TARGETOS
  TARGETOS := $(shell uname -s)
endif

#phyloP support enabled by default except on Mavericks, under which it won't build
#(same test as used in sonLib/include.mk)
ifneq ($(wildcard /usr/bin/clang),) 
	ENABLE_PHYLOP = 
else
	ENABLE_PHYLOP = 1
endif
