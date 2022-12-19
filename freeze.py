from AutoVASP import *
import sys

#this is a script that will freeze a POSCAR or CONTCAR file by a min_z set by a command line argument 

#read in the file as a command line argument
structure = structure_from_file(sys.argv[1])
min_z = int(sys.argv[2])
#freeze the structure
frozen_structure = freeze_structure(structure, min_z)

#write the extended structure to a file, the name of the file is the name of the original file with _extended
frozen_structure.to('POSCAR', sys.argv[1] + "_frozen")