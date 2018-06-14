# IMPORTANT: Progressive Cactus has moved here:
# [https://github.com/ComparativeGenomicsToolkit/cactus](https://github.com/ComparativeGenomicsToolkit/cactus)
# This version a) is actively maintained and developed and b) supports cloud computing platforms by using Toil in place of JobTree

#
#
# 
 
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
* wget
* ping
* 64bit processor and build environment
* 150GB+ of memory on at least one machine when aligning mammal-sized genomes; less memory is needed for smaller genomes.
* Parasol or SGE for cluster support.
* 750M disk space

### Instructions
Installing
-----

**IMPORTANT NOTE: Progressive Cactus does not presently support installation into paths that contain spaces.  Until this is resolved, you can use a softlink as a workaround: ln -s "path with spaces" "installation path without spaces"**

In the parent directory of where you want Progressive Cactus installed:

    git clone git://github.com/glennhickey/progressiveCactus.git
    cd progressiveCactus
    git pull
    git submodule update --init
    make

It is also convenient to add the location of `progressiveCactus/bin` to your PATH environment variable.  In order to run the included tools (ex hal2maf) in the submodules/ directory structure, first source `progressiveCactus/environment` to load the installed environment.

If any errors occur during the build process, you are unlikely to be able to use the tool. Please submit a GitHub issue so we can help out: not only will you help yourself, but others who wish to use the tool as well.

*Note that all dependencies are also built and included in the submodules/ directory.  This increases the size and build time but greatly simplifies installation and version management.  The installation does not create or modify any files outside the progressiveCactus/ directory.*

Updating the distribution
-----

To update a progressiveCactus installation, run the following:

    cd progressiveCactus
    git pull
    git submodule update --init
    make ucscClean
    make

This will update the installation and all the submodules it contains.

Using the progressiveCactus environment
-----
In order to avoid incompatibilities between python versions, and other libraries it depends on, progressiveCactus creates a virtual environment that must be loaded to use any of the tools in the package, except the aligner. Loading this environment temporarily modifies your session's PATH, PYTHONPATH, and other environment variables so that you're able to use the tools more easily.

To load this environment, run `source environment`, or, for non-bash shells, `. environment` in the main progressiveCactus directory.

To disable the environment, run `deactivate`. It's necessary to disable the environment before rebuilding progressiveCactus.

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
    nameN pathN

An optional * can be placed at the beginning of a name to specify that its assembly is of reference quality.  This implies that it can be used as an outgroup for sub-alignments.  If no genomes are marked in this way, all genomes are assumed to be of reference quality.  The star should only be placed on the name-path lines and not inside the tree.

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
	  # human, chimp and gorilla are flagged as good assemblies.  
	  # since orang isn't, it will not be used as an outgroup species.
     (((human:0.006,chimp:0.006667):0.0022,gorilla:0.008825):0.0096,orang:0.01831);
     *human /data/genomes/human/human.fa
     *chimp /data/genomes/chimp/
     *gorilla /data/genomes/gorilla/gorilla.fa
     orang /cluster/home/data/orang/
     
The sequences for each species are named by their fasta headers. To avoid ambiguity, the first word of each header must
be unique within its genome. Additionally, by default we check that the header is alphanumeric. We do this to ensure compatibility with visualisation tools, e.g. the UCSC browser. 
To disable this behaviour, remove the first preprocessor tag from the config.xml file that you use.

**`<workDir>`**

Working directory for the cactus aligner.  It will be created if it doesn't exist.  If an incomplete alignment is found in this directory for the same input data, Progressive Cactus will attempt to continue it (ie skip any ancestral genomes that were successfully reconstructed previously).  If this behavior is undesired, either erase the working directory or use the `--overwrite` option to restart from scratch. 

When running on a cluster, `<workDir>` must be accessible by all nodes.

**`<outputHalFile>`**

Location of the output alignment in HAL (Hierarchical ALignment) format.  This is a compressed file that can be accessed via the [HAL Tools](https://github.com/glennhickey/hal/blob/master/README.md)

### Resuming existing jobs

If Progressive Cactus detects that some sub-alignments in the working directory have already been successfully completed, it will skip them by default.  For example, if the last attempt crashed when aligning the human-chimp ancestor to gorilla, then rerunning will not recompute the human-chimp alignment.  To force re-alignment of already-completed subalignments, use the `--overwrite` option or erase the working directory. 

Progressive Cactus will always attempt to rerun the HAL exporter after alignmenet is completed, even if the alignment has not changed.

#### General Options

**`--configFile=CONFIGFILE`**

Location of progressive cactus configuration file in XML format.  The default configuration file can be found in `progressiveCactus/submodules/cactus/cactus_progressive_config.xml`.  These parameters are currently undocumented so modify at your own risk.

**`--legacy`**

Align all genomes at once.   This consistent with the original version of Cactus that this package was designed to replace. 

**`--autoAbortOnDeadlock`**         

Abort automatically when jobTree monitor suspects a deadlock by deleting the jobTree folder. Will guarantee no trailing ktservers but still  dangerous to use until we can more robustly detect  deadlocks.

**`--overwrite`**         

Re-align nodes in the tree that have already been successfully aligned.

### JobTree Options and Running on the Cluster

#### Running with more threads on a single machine
If you're running on a single machine, you can give your alignment run additional threads by supplying the `--maxThreads <N>` option to the aligner. The default is 4, so if you're running anything sizable, you'll definitely want to increase this!

#### Running on a cluster batch system
Currently, the cluster systems Parasol and Sun GridEngine are supported. PBS/Torque support has stalled. If you're interested in using PBS/Torque, let us know.

Hopefully, your cluster setup has at least one beefy machine with lots of RAM, and several additional compute nodes, which may have less RAM and/or compute power. In this case, you'll want to run progressiveCactus so that it runs the initial alignment (blast) and alignment refinement (bar) stages, which are highly parallelizable, on the cluster, and keep the cactus DB on a central server. A decent starting point for options to provide to the aligner is:

    --batchSystem <clusterSystem> --bigBatchSystem singleMachine --defaultMemory 8589934593 --bigMemoryThreshold 8589934592 --bigMaxMemory 893353197568 --bigMaxCpus 25 --maxThreads 25 --retryCount 3

where `<clusterSystem>` is either `parasol` or `gridengine`.

For more details, please see the [Jobtree Manual](https://github.com/benedictpaten/jobTree/blob/master/README.md).

Computation Time & Memory Usage
------

This code is under constant development and contains numerous different algorithms making a static assessment on computation time and memory usage difficult. However, to demonstrate the performance of progressiveCactus in practice the following is output from [jobTreeStats](https://github.com/benedictpaten/jobTree#running-and-examining-a-jobtree-script) for analysing the runtime for aligning 5 mammalian genomes:

```
[benedict@hgwdev tempProgressiveCactusAlignment]$ jobTreeStats --jobTree ./jobTree --pretty --sortCategory=time --sortField=total --sortReverse
Batch System: parasol
Default CPU: 1  Default Memory: 8.0G
Job Time: 30s  Max CPUs: 9.22337e+18  Max Threads: 25
Total Clock: 11m6s  Total Runtime: 20h11m51s
Slave
    Count |                                                     Time* |                                                      Clock |                                                    Wait |                                   Memory 
        n |       min      med      ave      max               total* |       min      med      ave      max                 total |      min     med      ave      max                total |      min     med     ave     max   total 
   270051 |        0s      96s    2m37s 16h52m7s 70weeks2days1h20m56s |        0s      95s    2m32s   5h5m9s 67weeks6days15h46m27s |       0s      1s       5s 16h52m6s 2weeks3days10h52m47s |    23.6M   23.6M   52.5M    8.0G   13.5T
Target
    Count |                                                     Time* |                                                      Clock |                                                    Wait |                                   Memory 
        n |       min      med      ave      max               total* |       min      med      ave      max                 total |      min     med      ave      max                total |      min     med     ave     max   total 
   292627 |        0s      90s    2m23s 16h52m7s 69weeks3days6h48m59s |        0s      89s    2m20s   5h5m2s  67weeks6days14h4m37s |       0s      0s       3s 16h52m6s   1week5days21h6m54s |    23.6M   23.6M   89.2M    8.0G   24.9T
 RunBlast
    Count |                                                     Time* |                                                      Clock |                                                    Wait |                                   Memory 
        n |       min      med      ave      max               total* |       min      med      ave      max                 total |      min     med      ave      max                total |      min     med     ave     max   total 
   230963 |        2s      95s     116s    12m2s  44weeks3days2h22m1s |        3s      94s     115s   11m50s   44weeks1day9h48m11s |       0s      0s       1s     2m4s        3days8h29m58s |    23.6M   23.6M   23.6M   23.6M    5.2T
 PreprocessChunk
    Count |                                                     Time* |                                                      Clock |                                                    Wait |                                   Memory 
        n |       min      med      ave      max               total* |       min      med      ave      max                 total |      min     med      ave      max                total |      min     med     ave     max   total 
     9413 |       34s   17m15s   17m11s   37m48s    16weeks0day9h4m6s |       33s   16m53s   16m50s    37m0s  15weeks5days3h18m26s |       0s     15s      20s    2m28s        2days5h45m58s |    24.7M   24.8M   24.8M   32.3M  227.6G
 CactusBarWrapper
    Count |                                                     Time* |                                                      Clock |                                                    Wait |                                   Memory 
        n |       min      med      ave      max               total* |       min      med      ave      max                 total |      min     med      ave      max                total |      min     med     ave     max   total 
    10381 |        0s    4m45s    5m57s   40m42s  6weeks0day23h35m39s |        0s    4m17s    5m38s   40m15s  5weeks5days16h21m45s |       0s     15s      19s     2m9s        2days7h13m53s |    34.3M   34.4M   41.5M  455.4M  420.6G
    ...
```

You'll see it took about a day of wall-clock time (**Total Runtime: 20h11m51s**) and just under 100 CPU days per genome aligned (**70weeks2days1h20m56s / 5 ~= 98 days**). This was run on a shared compute cluster with 1000 CPUs (actual usage was generally lower than 1000) and, for the large memory jobs, a machine with 64 CPUs and 1TB of RAM. The largest Target used around 100GB of ram, and total peak memory usage on the large memory machine was ~250GB of ram.

The dominent "Target" (that is the wrapper for a job in [jobTree](https://github.com/benedictpaten/jobTree/)) in terms of runtime was computing local alignments with [LastZ](http://www.bx.psu.edu/~rsharris/lastz/) for the CAF algorithm of Cactus (see the original [Cactus alignment paper](http://www.ncbi.nlm.nih.gov/pubmed/21665927) for a description), followed by steps to rigourlessly repeat mask the input genomes (the PreprocessChunk target stats), followed by the BAR algorithm steps (also described in that same paper). 

In terms of asymptotic scaling, progressive cactus will scale linearly in the number of input genomes, provided a phylogenetic tree is provided. If no tree is provided, or the tree is poorly resolved (e.g. a near star tree) then scaling is quadratic in the number of input genomes. In terms of input genome length scaling is approximately quadratic for megabase to gigabase genomes, but with the small coefficients associated with an efficient BLAST algorithm. For example, to align 66 E. coli/Shigella genomes without a phylogenetic tree, whose median length is only around 5 megabases is substantially quicker, despite the number of genomes:

```
]$ jobTreeStats --jobTree ./jobTree --pretty --sortCategory=time --sortField=total --sortReverse
Batch System: parasol
Default CPU: 1  Default Memory: 8.0G
Job Time: 30s  Max CPUs: 9.22337e+18  Max Threads: 25
Total Clock: 5m12s  Total Runtime: 17h10m17s
Slave
    Count |                                                  Time* |                                                   Clock |                                         Wait |                                   Memory 
        n |        min       med       ave       max        total* |        min       med       ave       max          total |      min     med      ave      max     total |      min     med     ave     max   total 
      349 |         0s    11m29s    18m29s  17h9m51s 4days11h32m1s |         0s    10m24s    14m12s 11h56m30s 3days10h38m29s |       0s      4s    4m16s 17h9m51s 24h53m47s |       0K      0K      0K      0K      0K
Target
 Slave Jobs   |     min    med    ave    max
              |       1      1      1      1
    Count |                                                  Time* |                                                   Clock |                                         Wait |                                   Memory 
        n |        min       med       ave       max        total* |        min       med       ave       max          total |      min     med      ave      max     total |      min     med     ave     max   total 
      824 |         0s        1s     7m49s  17h9m51s 4days11h29m8s |         0s        0s      6m1s 11h56m30s  3days10h38m9s |       0s      0s     108s 17h9m51s 24h51m50s |       0K      0K      0K      0K      0K
 RunBlast
    Count |                                                  Time* |                                                   Clock |                                         Wait |                                   Memory 
        n |        min       med       ave       max        total* |        min       med       ave       max          total |      min     med      ave      max     total |      min     med     ave     max   total 
       91 |       9m9s     23m9s    23m24s    43m35s 1day11h30m17s |      7m23s     22m1s    21m56s    38m35s    1day9h16m2s |       0s     61s      88s     5m0s  2h14m14s |       0K      0K      0K      0K      0K
 CactusBarEndAlignerWrapper
    Count |                                                  Time* |                                                   Clock |                                         Wait |                                   Memory 
        n |        min       med       ave       max        total* |        min       med       ave       max          total |      min     med      ave      max     total |      min     med     ave     max   total 
       69 |     17m39s    21m50s    22m55s    41m11s  1day2h21m26s |      15m8s    20m22s    20m57s    40m42s       24h6m20s |      17s     60s     117s    5m51s   2h15m5s |       0K      0K      0K      0K      0K
```

The total wall-clock runtime was around 17 hours (**17h10m17s**) and the total computation time was only just over 4 days (**4days11h32m1s**). 

One important final issue to note, progressive cactus is reasonably able to align genome assemblies consisting of 1000s or even hundreds of 1000s of contigs/scaffolds. The number of sequences should not significantly alter the runtimes (the mammalian genomes included an assembly with more than 50k scaffolds), though it may somewhat expand the resulting HAL file size.

Examples
------

Test data can be found in `progressiveCactus/submodules/cactusTestData`.  Example input sequence files are in `progressiveCactus/examples`.

*We assume unless otherwise specified that all commands are run from the `progressiveCactus/` installation directory.  This is primarily important because some of the example data contains relative paths*

### Default options

Align the small Blanchette alignment

    bin/runProgressiveCactus.sh examples/blanchette00.txt ./work ./work/b00.hal

### Export MAF

    bin/runProgressiveCactus.sh examples/blanchette00.txt ./work ./work/b00.hal 
    source ./environment && hal2mafMP.py ./work/b00.hal ./work/b00.hal.maf

### Use more threads

    bin/runProgressiveCactus.sh examples/blanchette00.txt ./work ./work/b00.hal --database kyoto_tycoon --maxThreads 10

HAL Tools
-----

The HAL tools and API let you examine your alignment after it's complete. Please see the [HAL Manual](https://github.com/glennhickey/hal/blob/master/README.md).  Note that all binaries are found in `progressiveCactus/submodules/hal/bin` and should be run after calling `source ./environment`

Credits
------

Progressive Cactus was developed in [*David Haussler*'s lab at UCSC](http://www.cbse.ucsc.edu/people/hausslerlab).  

* Progressive Cactus and HAL: *Glenn Hickey* hickey@soe.ucsc.edu, *Joel Armstrong* jcarmstr@ucsc.edu and *Ngan Nguyen* nknguyen@soe.ucsc.edu
* Cactus algorithm and JobTree: *Benedict Paten* benedict@soe.ucsc.edu

#### External Packages redistributed as git submodules

These packages are linked to via their github locations (or our mirror if they weren't already on github).  Apart from slight tweaks to the builds of Kyoto Tycoon and lastz, they have not been modified.  The source code and license information can be found in the `progressiveCactus/submodules` directoy.  The homepages are as follows:

* [Virtual Env](http://www.virtualenv.org/en/latest/index.html)
* [networkx](http://networkx.lanl.gov/)
* [psutil](http://code.google.com/p/psutil/)
* [biopython](http://http://biopython.org/)
* [bzip2](http://www.bzip.org/)
* [zlib](http://www.zlib.net/)
* [Kyoto Tycoon](http://fallabs.com/kyototycoon/)
* [Tokyo Cabinet](http://fallabs.com/tokyocabinet/)
* [Kyoto Cabinet](http://fallabs.com/kyotocabinet/)
* [HDF5](http://www.hdfgroup.org/HDF5/)
* [lastz](http://www.bx.psu.edu/~rsharris/lastz/)
* [pbs-drmaa](http://sourceforge.net/projects/pbspro-drmaa/)
* [drmaa-python](http://code.google.com/p/drmaa-python/)
* [clapack](http://www.netlib.org/clapack/)
* [phast](http://compgen.bscb.cornell.edu/phast/) (includes [pcre](http://www.pcre.org/))

We thank all the authors of the above for sharing their high quality free software with the community. 

#### Kent Binaries

The `hal2assemblyHub.py` script for making USCSC Genome Browser Comparative Assembly Hubs is dependent on a handful of Genome Browser tools.  These are downloaded as binaries automatically for convenience during installation.  Unlike the other included dependencies (listed above), **it is forbidden to use these binaries for anything other than academic, noncommercial, and personal use without obtaining a commercial license.**  For more information, see [http://hgdownload.cse.ucsc.edu/downloads.html#source_downloads](http://hgdownload.cse.ucsc.edu/downloads.html#source_downloads).   It is therefore forbidden to run `hal2assemblyHub.py` for commercial purposes without obtaining the license to run the Kent tools.


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

### Exception for binaries downloaded into submodules/kentToolBinaries by Make

The `hal2assemblyHub.py` script for making USCSC Genome Browser Comparative Assembly Hubs is dependent on a handful of Genome Browser tools.  These are downloaded as binaries automatically for convenience during installation.  Unlike the other included dependencies (listed above), **it is forbidden to use these binaries for anything other than academic, noncommercial, and personal use without obtaining a commercial license.**  For more information, see [http://hgdownload.cse.ucsc.edu/downloads.html#source_downloads](http://hgdownload.cse.ucsc.edu/downloads.html#source_downloads).   It is therefore forbidden to run `hal2assemblyHub.py` for commercial purposes without obtaining the license to run the Kent tools.
