from AutoVASP import *

file_prefix = "/home/wladerer/github/vaspy"
systems = ["Bi2Se3", "Bi2Te3", "Sb2Te3", "Sb2Se3"]
bi2se3 = f"{file_prefix}/Bi2Se3.vasp"
bi2te3 = f"{file_prefix}/Bi2Te3.vasp"
sb2se3 = f"{file_prefix}/Sb2Se3.vasp"
sb2te3 = f"{file_prefix}/Sb2Te3.vasp"

files = [bi2se3, bi2te3, sb2te3, sb2se3]
structures = [structure_from_file(f) for f in files]

#make a 3x3x1 supercell of each structure
extended_structures = [structure * [3,3,1] for structure in structures]

final_structures = [freeze_structure(structure, min_z=40) for structure in extended_structures]


jobs = [vaspInput(structure, job_types["slab_relaxation_med_prec"]) for structure in final_structures]

for i,job in enumerate(jobs):
    job.write_input_files(f"{systems[i]}_331_slab_relaxation_med_prec", readme=True)



