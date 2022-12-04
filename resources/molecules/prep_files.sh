#!/bin/bash

poscar_dir="/p/work1/wladerer/longer_frozen_tetrads/adsorbates/poscars"
#takes all poscar files in poscar_dir and puts them in to the corresponding directory
#the directory is named after the basename of the poscar file, omitting the .poscar extension
#incar and kpoints files are also copied to the directory
for poscar in $poscar_dir/*.poscar
do
    dir_name=$(basename $poscar .poscar)
    mkdir $dir_name
    cp $poscar $dir_name/POSCAR
    cp INCAR $dir_name/INCAR
    cp KPOINTS $dir_name/KPOINTS
    cp vasp.pbs $dir_name/vasp.pbs
done