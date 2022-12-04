#!/bin/bash

#this is a script that adds vacuum to a molecule in a POSCAR file

#lines 3, 4, and 5 are the lattice vectors
#all lines after 8 are the coordinates of the atoms

poscar=$1
new_vectors="15 0 0\n0 15 0\n0 0 15"
#replaces lines 3-5 of poscar with new_vectors
sed -i "3,5c$new_vectors" $poscar
