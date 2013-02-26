Progressive Cactus Manual
=====
*v0.0 by Glenn Hickey (hickey@soe.ucsc.edu)*

Progressive Cactus is a whole-genome alignment package.  

Installation
-----

### Requirements
* git
* gcc 4.2 or newer
* python 2.7
* 64bit processor and build environment
* Parasol or SGE or Torque (see below) for cluster support.
* 750M disk space

### PBS/Torque Cluster Support

In order to run on clusters with the PBS / Torque resource manager, change the `enablePBSTorque` variable at the bottom of the `submodules/include.mk` file from `no` to `yes` before running make in the instructions below (*functionality is still being tested and developed*)

### Instructions
In the parent directory of where you want Progressive Cactus installed:

    git clone git://github.com/glennhickey/progressiveCactus.git
    cd progressiveCactus
    git pull
    git submodule update --init
    make

It is also convenient to add the location of `progressiveCactus/bin` to your PATH environment variable.  In order to run the included tools (ex hal2maf) in the submodules/ directory structure, first source `progressiveCactus/environment` to load the installed environment.

If any errors occur during the build process, you are unlikely to be able to use the tool.

*Note that all dependencies are also built and included in the submodules/ directory.  This increases the size and build time but greatly simplifies installation and version management.  The installation does not create or modify any files outside the progressiveCactus/ directory. *  

Running the aligner
-----

### runProgressiveCactus.sh

The aligner is run using the `bin/runProgressiveCactus.sh` script in the installation directory.  Details about the command line interface can be obtained as follows:

    bin/runProgressiveCactus.sh --help

Usage: `runProgressiveCactus.sh [options] <seqFile> <workDir> <outputHalFile>`

### Required arguments

**`<seqFile>`**   

Text file containing the locations of the input sequences as well as their phylogenetic tree.  The tree will be used to progressively decompose the alignment by iteratively aligning sibling genomes to estimate their parents in a bottom-up fashion. If the tree is not specified, then a star-tree will be assumed (a single root with all leaves connected to it) and all genomes will be aligned together at once.  The file is formatted as follows:

    NEWICK tree (optional)
    name1 path1
    name2 path2
    ...
    nameN nameN

* The tree, if specified, must be on a single line.  All leaves must be labeled and these labels must be unique.  Labels should not contain any spaces.
* Branch lengths that are not specified are assumed to be 1
* Lines beginning with # are ignored. 
* Sequence paths must point to either a FASTA file or a directory containing 1 or more FASTA files.
* Sequence paths must not contain spaces.
* Sequence paths that are not referred to in the tree are ignored
* Leaves in the tree that are not mapped to a path are ignored
* Each name / path pair must be on its own line
* Paths must be absolute

Example:
     
	  # Sequence data for progressive alignment of 4 genomes
     (((human:0.006,chimp:0.006667):0.0022,gorilla:0.008825):0.0096,orang:0.01831);
     human /data/genomes/human/human.fa
     chimp /data/genomes/chimp/
     gorilla /data/genomes/gorilla/gorilla.fa
     orang /cluster/home/data/orang/

**`<workDir>`**

Working directory for the cactus aligner.  It will be created if it doesn't exist.  Ideally it should be empty.  If it isn't, its contents may be overwritten.  If Progressive Cactus finds evidence of a partially completed alignment in the working directory, it will try to resume this job (a message will be printed).  To avoid this, make sure the directory is empty. 

When running on a cluster, `<workDir>` must be accessible by all nodes.

**`<outputHalFile>`**

Location of the output alignment in HAL (Hierarchical ALignment) format.  This is a compressed file that can be accessed via the [HAL Tools](https://github.com/glennhickey/hal/blob/master/README.md)

#### General Options

**`--configFile=CONFIGFILE`**

Location of progressive cactus configuration file in XML format.  The default configuration file can be found in `progressiveCactus/submodules/cactus/progressive/cactus_progressive_workflow_config.xml`.  These parameters are currently undocumented so modify at your own risk.

**`--outputMaf=OUTPUTMAF`**

Create a MAF version of the multiple alignment in the desired location in addition to the HAL file.  This option may drastically increase the space, time and memory required to perform a progressive alignment: Consider using `progressiveCactus/submodules/hal/hal2maf` on the output hal file instead. 

**`--database=DATABASE`**

Select the type of database from either `tokyo_cabinet` or `kyoto_tycoon` (see below).  `kyoto_tycoon` is necessary to obtain speedup from most types of parallelism and therefore recommended for larger alignments.  `tokyo_cabinet` is simpler as no server processes are created but is only useful for testing the basic installation on small examples.

**`--legacy`**

Align all genomes at once.   This consistent with the original version of Cactus that this package was designed to replace. 

### Database Options

During alignment, a cactus graph is built and maintained in a database.  Two types of databasese are supported for this task: Tokyo Cabinet and Kyoto Tycoon.  They are freely available from [Fal Labs](http://fallabs.com/) and mirrored in the Progressive Cactus installation directory. 

####Tokyo Cabinet

This is the default and simplest option.  The cactus graphs are stored on disk (in `<workDir>`).  Since parallel write access is limited, Tokyo Cabinet is only practical for very small test alignments.

####Kyoto Tycoon

Available by default (orwith the `--database kyoto_tycoon`) command line option.  Kyoto Tycoon databases are kept *in memory* and are accessed via a client-server model.  Both parallel reads and writes are supported.   It is best to leave all the Kyoto Tycoon-related options (`--kt*`) alone unless you are an expert.  

*The scripts do their best to clean them up, but it is possible that trailing ktserver daemons linger after certain crash situations.  One way to clear them is to delete the contents of `workdDir/jobTree`

### JobTree Options and Running on the Cluster

(to do)

For more details, please see the [Jobtree Manual](https://github.com/benedictpaten/jobTree/blob/master/README.md).

Examples
------

Test data can be found in `progressiveCactus/submodules/cactusTestData`.  Example input sequence files are in `progressiveCactus/examples`

*We assume unless otherwise specified that all commands are run from the `progressiveCactus/` installation directory.  This is primarily important because some of the example data contains relative paths*

### Default options

Align the small Blanchette alignment

    bin/runProgressiveCactus.sh examples/blanchette00.txt ./work ./work/b00.hal

### Export MAF

    bin/runProgressiveCactus.sh examples/blanchette00.txt ./work ./work/b00.hal --outputMaf ./work/b00.maf

### Use kyoto_tycoon

    bin/runProgressiveCactus.sh examples/blanchette00.txt ./work ./work/b00.hal --database kyoto_tycoon

### Use more threads

    bin/runProgressiveCactus.sh examples/blanchette00.txt ./work ./work/b00.hal --database kyoto_tycoon --maxThreads 10

HAL Tools
-----

Please see the [HAL Manual](https://github.com/glennhickey/hal/blob/master/README.md).  Note that all binaries are found in `progressiveCactus/submodules/hal/bin`

Credits
------

Progressive Cactus was developed in [*David Haussler*'s lab at UCSC](http://www.cbse.ucsc.edu/people/hausslerlab).  

* Progressive Cactus and HAL: *Glenn Hickey* hickey@soe.ucsc.edu
* Cactus algorithm and JobTree: *Benedict Paten* benedict@soe.ucsc.edu
* MAF tools: *Dent Earl* dearl@soe.ucsc.edu

#### External Packages redistributed as git submodules

These packages are linked to via their github locations (or our mirror if they weren't already on github).  Apart from slight tweaks to the builds of Kyoto Tycoon and lastz, they have not been modified.  The source code and license information can be found in the `progressiveCactus/submodules` directoy.  The homepages are as follows:

* [Virtual Env](http://www.virtualenv.org/en/latest/index.html)
* [networkx](http://networkx.lanl.gov/)
* [psutil](http://code.google.com/p/psutil/)
* [bzip2](http://www.bzip.org/)
* [zlib](http://www.zlib.net/)
* [Kyoto Tycoon](http://fallabs.com/kyototycoon/)
* [Tokyo Cabinet](http://fallabs.com/tokyocabinet/)
* [Kyoto Cabinet](http://fallabs.com/kyotocabinet/)
* [HDF5](http://www.hdfgroup.org/HDF5/)
* [lastz](http://www.bx.psu.edu/~rsharris/lastz/)
* [pbs-drmaa](http://sourceforge.net/projects/pbspro-drmaa/)
* [drmaa-python](http://code.google.com/p/drmaa-python/)

We thank all the authors of the above for sharing their high quality free software with the community.  

Citing
------

Manuscript in preparation.  Cactus can be cited by:

* *Paten et al.  Cactus: Algorithms for genome multiple sequence alignment, Genome Research, 21:9, 1512-1528, 2011.*

* *Paten et al.  Cactus graphs for genome comparisons},  Journal of Computational Biology, 18:3, 169-481, 2011.*

Copyright
------
*Please see the LICENSE of each submodule for its copyright information.  The UCSC packages are released under the MIT license, but we release this distribution package under the GPL because some of the external packages use this more restrictive license.*

Copyright (C) 2009-2012 by Glenn Hickey (hickey@soe.ucsc.edu) and Benedict Paten (benedict@soe.ucsc.edu)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the [GNU General Public License](LICENSE)
along with this program.  If not, see <http://www.gnu.org/licenses/>.
