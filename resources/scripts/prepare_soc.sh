#!/bin/bash

#this is a script to prepare SOC calculations from a converged vasp calculation

mkdir soc
cd soc || exit

cp ../CONTCAR POSCAR
cp ../INCAR_soc INCAR
cp ../KPOINTS_soc KPOINTS
cp ../POTCAR .

noncollinear 
