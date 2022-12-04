#!/bin/bash

#Written by William Laderer, 2022
#UCLA Department of Chemistry and Biochemistry

noncollinear_error() {
    echo "Error might be due to WAVECAR not being noncollinear. Please check your WAVECAR file."
    echo "If you are using a noncollinear WAVECAR, please check your INCAR file."
    echo "Renaming WAVECAR to WAVECAR.old and restarting the job."
    mv WAVECAR WAVECAR.old
    noncollinear
}

while getopts 'bp:' OPTION; do
  case "$OPTION" in
    b)
      echo "Including band decomposed charge densities in multiple directories"
      export bdcd_incar=$OPTARG
      export bdcd_dir=BDCD
      export b=true
      ;;
    p)
      echo "Using python script to generate INCARs"
      python3 "$OPTARG" || exit 
      ;;
    # a)
    #   avalue="$OPTARG"
    #   echo "The value provided is $OPTARG"
    #   ;;
    ?)
      echo "script usage: $(basename \$0) [-b] [-h] [-a somevalue]" >&2
      exit 1
      ;;
  esac
done
shift "$(($OPTIND -1))"

#This is a script that takes a POSCAR file and runs a geometry relaxation using multiple configurations of INCAR files
#Runs until slabs have been analyzed

#This script is designed to be run from the directory containing the POSCAR file


HOME=/home/ #change this to the home directory of the user running the script
start_date=$(date +%Y-%m-%d)
progress_file=$HOME/vasp_progress_$start_date.txt
data_file=data_file_$start_date.csv
echo JobType,Atoms,Energy,Electrons,Bands,NKpoints,Kx,Ky,Kz > "$data_file"

#add the directory to the progress file
{   echo "{Running in directory: $(pwd)" 
    #add the formula to the progress file
    echo "Formula: $(grep -m 1 -o -E '[A-Z][a-z]*' POSCAR)" 
    #add the number of atoms to the progress file
    echo "Number of atoms: $(grep -m 1 -o -E '[0-9]+' POSCAR)" 
} >> "$progress_file"

module load VASP
cd "$PBS_O_WORKDIR" || exit

soc_dir=SOC
mbj_dir=MBJ
band_dir=BAND
dos_dir=DOS
lobster_dir=LOBSTER
dirs=( "$soc_dir" "$mbj_dir" "$band_dir" "$dos_dir" )

#check to see if subdirectories exist
echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Checking for subdirectories" >> "$progress_file"
for dir in "${dirs[@]}"
do
    if [ ! -d "$dir" ]; then
        mkdir "$dir"
    fi
done

soc_incar=INCAR_SOC
mbj_incar=INCAR_MBJ
band_incar=INCAR_BAND
dos_incar=INCAR_DOS
kpath=kpath
lobster_in=lobsterin
incars=( "$soc_incar" "$mbj_incar" "$band_incar" "$dos_incar" "$kpath" )

#Check if INCAR files exist, if not, notify user and exit
echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Checking for INCAR files" >> "$progress_file"
for incar in "${incars[@]}"; do
    if [ ! -f "$incar" ]; then
        echo "INCAR file $incar does not exist. Please create it and try again."
        exit 1
    fi
done

#Check if directories exist, if not, create them
echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Creating directories" >> "$progress_file"
for dir in "${dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir "$dir"
    fi
done

# copy incars to their respective directories

for incar in "${incars[@]}"; do
    if [ "$incar" == "$kpath" ]; then
        cp "$incar" "$band_dir"
    else
        cp "$incar" "$dir"/INCAR
    fi
done

#if potcar exists, copy it to all directories
echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Copying POTCAR to all directories" >> "$progress_file"
if [ -f POTCAR ]; then
    for dir in "${dirs[@]}"; do
        cp POTCAR "$dir"
    done
fi

#create a BAND directory in the SOC and MBJ directories

mkdir "$soc_dir"/"$band_dir"; cp "$band_incar" "$soc_dir"/"$band_dir"; cp "$kpath" "$soc_dir"/"$band_dir"
mkdir "$mbj_dir"/"$band_dir"; cp "$band_incar" "$mbj_dir"/"$band_dir"; cp "$kpath" "$mbj_dir"/"$band_dir"

#make a dos dir in the SOC directory
mkdir "$soc_dir"/"$dos_dir"; cp "$dos_incar" "$soc_dir"/"$dos_dir"

#create a LOBSTER directory in all dos directories
mkdir "$soc_dir"/"$dos_dir"/LOBSTER; cp "$lobster_in" "$soc_dir"/"$dos_dir"/LOBSTER
mkdir "$mbj_dir"/"$dos_dir"/LOBSTER; cp "$lobster_in" "$mbj_dir"/"$dos_dir"/LOBSTER

#copy KPOINTS file to all directories and subdirectories other than LOBSTER and BAND
echo "Copying KPOINTS file to all directories" >> "$progress_file"
for dir in "${dirs[@]}"; do
    if [ "$dir" != "$lobster_dir" ] && [ "$dir" != "$band_dir" ]; then
        cp KPOINTS "$dir"
    fi
done

vasp 

#check to see if OUTCAR did not converge using grep
if grep -q "reached required accuracy" OUTCAR; then
    echo "OUTCAR converged" >> "$progress_file"
else
    echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : OUTCAR did not converge" >> "$progress_file"
    exit 1
fi

#check to see if CONTCAR exists, if not, notify user and exit
if [ ! -f CONTCAR ]; then
    echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : CONTCAR does not exist. Please check your OUTCAR file and try again." >> "$progress_file"
    exit 1
fi


#copy CONTCAR to all directories and subdirectories as POSCAR
#update progress file with "CONTCAR moving to other directories"
echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Moving CONTCAR to other directories" >> "$progress_file"
for dir in "${dirs[@]}"; do
    if [ "$dir" != "$lobster_dir" ] && [ "$dir" != "$band_dir" ]; then
        cp CONTCAR "$dir"/POSCAR
    fi
done

#run vasp in all directories other than LOBSTER and SOC
for dir in "${dirs[@]}"; do
    if [ "$dir" != "$lobster_dir" ] && [ "$dir" != "$soc_dir" ]; then
        ( cd "$dir" || exit
        #update progress file with "Running in directory: $dir"
        echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Running in directory: $dir" >> "$progress_file"
        vasp )
    fi
done

#run noncollinear vasp in all SOC directories

( cd "$soc_dir" || exit
#update the progress file with "Running SOC in directory: $(pwd)"
cp ../WAVECAR ./ ; cp ../CHGCAR ./
#if the string "{bands}" is found in the INCAR file, replace it with two times the result of grep NBANDS | tail -1 | awk '{print $3}' OUTCAR
if grep -q "{bands}" INCAR; then
    sed -i "s/{bands}/$(grep NBANDS OUTCAR | tail -1 | awk '{print $3*2}')/g" INCAR
fi
echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Running SOC in directory: $(pwd)" >> "$progress_file"
noncollinear || noncollinear_error || exit 1 )

#run lobster in all lobster directories

for dir in "${dirs[@]}"; do
    if [ "$dir" == "$lobster_dir" ]; then
        ( cd "$dir" || exit
        #update the progress file with "running lobster in $dir"
        echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Running lobster in $dir" >> "$progress_file"
        lobster )
    fi
done

#compare the DOSCAR files in the SOC and MBJ directories
#update the progress file with "Comparing DOSCAR files"
echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Comparing DOSCAR files" >> "$progress_file"

if cmp -s "$soc_dir"/"$dos_dir"/DOSCAR "$mbj_dir"/"$dos_dir"/DOSCAR; then
    echo "DOSCAR files are the same" >> "$progress_file"
else
    echo "DOSCAR files are different" >> "$progress_file"
fi

#if b flag is set, create a BDCD directory in the parent, SOC, and MBJ directories
if [ "$b" == "true" ]; then
    mkdir "$bdcd_dir"; cp "$bdcd_incar" "$bdcd_dir"
    mkdir "$soc_dir"/"$bdcd_dir"; cp "$bdcd_incar" "$soc_dir"/"$bdcd_dir"
    mkdir "$mbj_dir"/"$bdcd_dir"; cp "$bdcd_incar" "$mbj_dir"/"$bdcd_dir"
fi

#run vasp in the mbj_bdcd directory and bdcd directory
if [ "$b" == "true" ]; then
    (cd "$mbj_dir"/"$bdcd_dir" || exit
    #update the progress file with "Running vasp in $mbj_dir/$bdcd_dir"
    echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Running vasp in $mbj_dir/$bdcd_dir" >> "$progress_file"
    vasp
    cd ../..
    cd "$bdcd_dir" || exit
    #update the progress file with "Running vasp in $bdcd_dir"
    echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Running vasp in $bdcd_dir" >> "$progress_file"
    vasp )
fi

#run noncollinear vasp in the soc_bdcd directory
if [ "$b" == "true" ]; then
    (cd "$soc_dir"/"$bdcd_dir" || exit
    #update the progress file with "Running noncollinear vasp in $soc_dir/$bdcd_dir"
    echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Running noncollinear vasp in $soc_dir/$bdcd_dir" >> "$progress_file"
    noncollinear || noncollinear_error || exit 1 )
fi

#iterate through all directories and subdirectories other than LOBSTER, DOS, and BAND to collect information in a csv file

#update the progress file with "Collecting information"
echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Collecting information" >> "$progress_file"

finished_job_dirs=( "./" "$mbj_dir" "$soc_dir" )
for dir in "${finished_job_dirs[@]}"; do
    ( cd "$dir" || exit
    #get the directory name and save as job_type
    job_type=$(basename "$PWD")
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
    #write information to $data_file.csv
    echo "$job_type,$atoms,$energy,$electrons,$bands,$kpoints,$kx,$ky,$kz" >> "$data_file")
done


# The final directory structure should look like the following tree diagram
# .
# ├── BAND
# │   ├── band_structure_files
# ├── BDCD
# │   ├── OUTCAR
# │   ├── vasprun.xml
# │   ├── ...
# ├── DOS
# │   ├── DOSCAR
# │   ├── OUTCAR
# │   ├── vasprun.xml
# │   ├── ...
# ├── LOBSTER
# │   ├── OUTCAR
# │   ├── vasprun.xml
# │   ├── ...
# ├── MBJ
# │   ├── BDCD
# │   │   ├── OUTCAR
# │   │   ├── vasprun.xml
# │   │   ├── ...
# │   ├── DOS
# │   │   ├── DOSCAR
# │   │   ├── OUTCAR
# │   │   ├── vasprun.xml
# │   │   ├── ...
# │   ├── OUTCAR
# │   ├── vasprun.xml
# │   ├── ...
# ├── SOC
# │   ├── BDCD
# │   │   ├── OUTCAR
# │   │   ├── vasprun.xml
# │   │   ├── ...
# │   ├── DOS
# │   │   ├── DOSCAR
# │   │   ├── OUTCAR
# │   │   ├── vasprun.xml
# │   │   ├── ...
# │   ├── OUTCAR
# │   ├── vasprun.xml
# │   ├── ...
# ├── INCAR
# ├── KPOINTS
# ├── POSCAR
# ├── POTCAR
# ├── progress.txt
# └── data.csv

#A sample data.csv file would look like the following
#job_type,atoms,energy,electrons,bands,kpoints,kx,ky,kz
#.,128,-0.000000,128.000000,128,128,1,1,1
#MBJ,128,-0.000000,128.000000,128,128,1,1,1
#SOC,128,-0.000000,128.000000,128,128,1,1,1

#A sample progress.txt file would look like the following
#[ 2018-10-26-17:42:17 ] : Running vasp in .
#[ 2018-10-26-17:42:17 ] : Running vasp in MBJ
#[ 2018-10-26-17:42:17 ] : Running vasp in SOC
#[ 2018-10-26-17:42:17 ] : Running noncollinear vasp in SOC
#[ 2018-10-26-17:42:17 ] : Running lobster in LOBSTER
#[ 2018-10-26-17:42:17 ] : Comparing DOSCAR files
#[ 2018-10-26-17:42:17 ] : Running vasp in MBJ/BDCD
#[ 2018-10-26-17:42:17 ] : Running vasp in BDCD
#[ 2018-10-26-17:42:17 ] : Running noncollinear vasp in SOC/BDCD
#[ 2018-10-26-17:42:17 ] : Collecting information
#[ 2018-10-26-17:42:17 ] : Finished


mkdir final_files
cp "$data_file" final_files
cp "$progress_file" final_files

#copy the subdirectories to the final_files directory, excluding 
# WAVECAR, CHG, CHGCAR, vasprun.xml
find . -maxdepth 1 -type d -not -name "final_files" -not -name ".*" -not -name "WAVECAR" -not -name "CHG" -not -name "CHGCAR" -not -name "vasprun.xml" -exec cp -r {} final_files \;

#archive the final_files directory
echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Archiving" >> "$progress_file"
tar -czvf final_files.tar.gz final_files

#remove the final_files directory
rm -rf final_files
echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Finished" >> "$progress_file"
echo "[ (date +%Y-%m-%d-%H:%M:%S) ] : Congrats, you made it to the end :)" >> "$progress_file"


