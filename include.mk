#Modify this variable to set the location of sonLib
sonLibRootPath=submodules/sonLib
sonLibPath=${sonLibRootPath}/lib

#cflags += -I ${sonLibPath} ${tokyoCabinetIncl} ${kyotoTycoonIncl} ${mysqlIncl} ${pgsqlIncl}

cflags = -I ${sonLibPath}
basicLibs = ${sonLibPath}/sonLib.a ${sonLibPath}/cuTest.a ${dblibs}
basicLibsDependencies = ${sonLibPath}/sonLib.a ${sonLibPath}/cuTest.a 
