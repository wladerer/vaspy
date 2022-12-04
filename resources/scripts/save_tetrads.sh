#!/bin/bash

#this script is used to save vasp output files
#the directory structure will be preserved
#the whole directory will be saved in a tar.gz file with a readme file
#the readme file contains the information of the calculation
#the tar.gz file will be saved in the current directory
#the name of the tar.gz file is the name of the current directory

declare -a systems=( "Bi2Se3" "Bi2Te3" "Sb2Se3" "Sb2Te3" )
declare -a planes=( "001" "010" "100" "111" )
#directory structure is as follows: system/plane 

mkdir tetrad_output
#make subdirectories to match the directory structure
for system in ${systems[@]}
do
    mkdir tetrad_output/$system
    for plane in ${planes[@]}
    do
        mkdir tetrad_output/$system/$plane
    done
done

#copy the output files to the corresponding subdirectories
for system in ${systems[@]}
do
    for plane in ${planes[@]}
    do
        cp $system/$plane/OUTCAR tetrad_output/$system/$plane
        cp $system/$plane/vasprun.xml tetrad_output/$system/$plane
        cp $system/$plane/CONTCAR tetrad_output/$system/$plane
        cp $system/$plane/POSCAR tetrad_output/$system/$plane
        cp $system/$plane/INCAR tetrad_output/$system/$plane
        #copy ELFCAR if it exists
        if [ -f $system/$plane/ELFCAR ]; then
            cp $system/$plane/ELFCAR tetrad_output/$system/$plane
        fi

        #copy CHGCAR if it exists
        if [ -f $system/$plane/CHGCAR ]; then
            cp $system/$plane/CHGCAR tetrad_output/$system/$plane
        fi

        #change to the subdirectory
        cd $system/$plane || exit

        #create a readme file for each calculation

        echo "System: $system" > readme
        echo "Plane: $plane" >> readme
        #get the number of atoms
        atoms=$(grep "NIONS" OUTCAR | awk '{print $12}')
        #Get the final energy
        energy=$(grep "TOTEN" OUTCAR | tail -1 | awk '{print $5}')
        #Get the number of electrons
        electrons=$(grep "NELECT" OUTCAR | awk '{print $3}')
        #Get the number of bands
        bands=$(grep "NBANDS" OUTCAR | awk '{print $15}')
        #Get the number of k-points
        kpoints=$(grep "NKPTS" OUTCAR | awk '{print $4}')
        #Get the fourth line of the KPOINTS file
        k=$(sed -n '4p' KPOINTS)
        #Get the Kx, Ky, and Kz values
        kx=$(echo "$k" | awk '{print $1}')
        ky=$(echo "$k" | awk '{print $2}')
        kz=$(echo "$k" | awk '{print $3}')

        echo "Number of atoms: $atoms" >> readme
        echo "Final energy: $energy" >> readme
        echo "Number of electrons: $electrons" >> readme
        echo "Number of bands: $bands" >> readme
        echo "Number of k-points: $kpoints" >> readme
        echo "Kx: $kx" >> readme
        echo "Ky: $ky" >> readme
        echo "Kz: $kz" >> readme

        cp readme ../../tetrad_output/$system/$plane

        #change back to the parent directory
        cd ../.. || exit
    done
done

#tar the output files
tar -czvf tetrad_output.tar.gz tetrad_output
#remove the directory
rm -r tetrad_output



