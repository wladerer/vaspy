from AutoVASP import *
import sys

#this is a script that will extend a POSCAR or CONTCAR file by a factor of 3 in the xy plane

#read in the file as a command line argument
structure = structure_from_file(sys.argv[1])
extended_structure = extend_structure(structure, 3, 3, 1)

#write the extended structure to a file, the name of the file is the name of the original file with _extended
extended_structure.to('POSCAR', sys.argv[1] + "_extended")