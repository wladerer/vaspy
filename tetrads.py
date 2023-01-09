from AutoVASP import *
from pymatgen.core.structure import Structure

# bi2se3_mpi_code = "mp-541837"
# bi2te3_mpi_code = "mp-34202"
# sb2se3_mpi_code = "mp-2160"
# sb2te3_mpi_code = "mp-1201"

# bi2se3 = structure_from_mpi_code(bi2se3_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")
# bi2te3 = structure_from_mpi_code(bi2te3_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")
# sb2se3 = structure_from_mpi_code(sb2se3_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")
# sb2te3 = structure_from_mpi_code(sb2te3_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")

# structures = [bi2se3, bi2te3, sb2se3, sb2te3]
# names = ["Bi2Se3", "Bi2Te3", "Sb2Se3", "Sb2Te3"]
# inputs = [vaspInput(structure, job_types["bulk_relaxation_high_prec"]) for structure in structures]

bi2se3 = structure_from_file("bs_bulk.vasp")
bi2te3 = structure_from_file("bt_bulk.vasp")
sb2se3 = structure_from_file("ss_bulk.vasp")
sb2te3 = structure_from_file("st_bulk.vasp")

structures = [bi2se3, bi2te3, sb2se3, sb2te3]

bs_slabs = slabs_from_structure(bi2se3, [0,0,1], min_slab_size=3, min_vacuum_size=3, use_in_unit_planes=True, ensure_symmetric_slabs=True) 
bt_slabs = slabs_from_structure(bi2te3, [0,0,1], min_slab_size=3, min_vacuum_size=3, use_in_unit_planes=True, ensure_symmetric_slabs=True)
ss_slabs = slabs_from_structure(sb2se3, [0,0,1], min_slab_size=2, min_vacuum_size=3, use_in_unit_planes=True, ensure_symmetric_slabs=True)
st_slabs = slabs_from_structure(sb2te3, [0,0,1], min_slab_size=3, min_vacuum_size=3, use_in_unit_planes=True, ensure_symmetric_slabs=True)

all_slabs = [bs_slabs, bt_slabs, ss_slabs, st_slabs]

extended_slabs = [slab[0] * [3,3, 1] for slab in all_slabs]
inputs = [vaspInput(slab, job_types["slab_relaxation_high_prec"]) for slab in extended_slabs]
prefixes = ["bs", "bt", "ss", "st"]

names = [f"{prefix}_3ql_slab" for prefix in prefixes]

for i, input in enumerate(inputs):
    input.write_input_files(f"{names[i]}", readme=True)