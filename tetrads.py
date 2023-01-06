from AutoVASP import *

bi2se3_mpi_code = "mp-541837"
bi2te3_mpi_code = "mp-34202"
sb2se3_mpi_code = "mp-2160"
sb2te3_mpi_code = "mp-1201"

bi2se3 = structure_from_mpi_code(bi2se3_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")
bi2te3 = structure_from_mpi_code(bi2te3_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")
sb2se3 = structure_from_mpi_code(sb2se3_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")
sb2te3 = structure_from_mpi_code(sb2te3_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")

structures = [bi2se3, bi2te3, sb2se3, sb2te3]
names = ["Bi2Se3", "Bi2Te3", "Sb2Se3", "Sb2Te3"]
inputs = [vaspInput(structure, job_types["bulk_relaxation_high_prec"]) for structure in structures]

for i,inp in enumerate(inputs):
    inp.write_input_files(names[i], readme=True)

