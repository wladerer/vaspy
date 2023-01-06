from AutoVASP import *

b2mo_mpi_code = "mp-2331" #166
wp2_mpi_code = "mp-11328" #36
wte2_mpi_code = "mp-22693" #31
ti2ga3_mpi_code = "mp-30673" #83


b2mo = structure_from_mpi_code(b2mo_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")
wp2 = structure_from_mpi_code(wp2_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")
wte2 = structure_from_mpi_code(wte2_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")
ti2ga3 = structure_from_mpi_code(ti2ga3_mpi_code, "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH")

structures = [b2mo, wp2, wte2, ti2ga3]
names = ["B2Mo", "Wp2", "WTe2", "Ti2Ga3"]

inputs = [vaspInput(structure, job_types["bulk_relaxation_high_prec"]) for structure in structures]

for i,inp in enumerate(inputs):
    inp.write_input_files(names[i], readme=True)

#tar the directories
import os
for name in names:
    os.system(f"tar -cvzf exploratory.tar.gz {names[0]} {names[1]} {names[2]} {names[3]}")
    