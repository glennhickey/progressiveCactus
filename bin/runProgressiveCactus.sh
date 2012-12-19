#!/bin/bash 

# Progressive Cactus Package
# Copyright (C) 2009-2012 by Glenn Hickey (hickey@soe.ucsc.edu)
# and Benedict Paten (benedictpaten@gmail.com)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

binDir=$(dirname $0)
envFile=${binDir}/../environment

# need to go through this monkey business to make sure arguments with spaces
# don't get split when passing to python 
options=""
i=1
for arg in "$@"
do
	 options="$options '${arg}'"
	 let "i+=1"
done
echo $options
. ${envFile} && eval python ${binDir}/../src/progressiveCactus.py "$options"
exit
