import AutoVASP as av
key = "UKRQAw2HZOkwJBpGh96V8zKFXGYLSIVH"
wp2_struct = av.structure_from_mpi_code("mp-11328", key)
wte2_struct = av.structure_from_mpi_code("mp-22693", key)

wp2 = av.vaspInput(wp2_struct, av.job_types["bulk_relaxation_high_prec"])
wte2 = av.vaspInput(wte2_struct, av.job_types["bulk_relaxation_high_prec"])

wp2.write_input_files()
wte2.write_input_files()
