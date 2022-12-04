#!/bin/bash 

#this is a script that archives all directories in the current directory that contain an OUTCAR file that contains "reached required accuracy"

#find all directories that contain an OUTCAR file that contains "reached required accuracy" and save these directories to an array
dirs=($(find . -name "OUTCAR" -exec grep -l "reached required accuracy" {} \; | sed 's/\/OUTCAR//g' | sed 's/^\.\///g' ))

basename=$(basename "$PWD")

#make a directory called "basename"_archive if it doesn't already exist
if [ ! -d "${basename}_archive" ]; then
    mkdir "${basename}_archive"
fi

#make all directories in the array
for dir in ${dirs[@]}; do
    mkdir "${basename}_archive"/"$dir"
done

#iterate over all the directories in than arrat and move INCAR, KPOINTS, POSCAR, CONTCAR, OUTCAR, vasprun.xml, ELFCAR, and DOSCAR to the corresponding directory in the archive

for dir in ${dirs[@]}; do
    if [ -f "$dir"/INCAR ]; then
        mv "$dir"/INCAR "${basename}_archive"/"$dir"/INCAR
    fi
    if [ -f "$dir"/KPOINTS ]; then
        mv "$dir"/KPOINTS "${basename}_archive"/"$dir"/KPOINTS
    fi
    if [ -f "$dir"/POSCAR ]; then
        mv "$dir"/POSCAR "${basename}_archive"/"$dir"/POSCAR
    fi
    if [ -f "$dir"/CONTCAR ]; then
        mv "$dir"/CONTCAR "${basename}_archive"/"$dir"/CONTCAR
    fi
    if [ -f "$dir"/OUTCAR ]; then
        mv "$dir"/OUTCAR "${basename}_archive"/"$dir"/OUTCAR
    fi
    if [ -f "$dir"/vasprun.xml ]; then
        mv "$dir"/vasprun.xml "${basename}_archive"/"$dir"/vasprun.xml
    fi
    if [ -f "$dir"/ELFCAR ]; then
        mv "$dir"/ELFCAR "${basename}_archive"/"$dir"/ELFCAR
    fi
    if [ -f "$dir"/DOSCAR ]; then
        mv "$dir"/DOSCAR "${basename}_archive"/"$dir"/DOSCAR
    fi
done

#archive the new archive directory
tar -cvzf "${basename}_archive".tar.gz "${basename}_archive"

