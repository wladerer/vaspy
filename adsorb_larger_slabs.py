from AutoVASP import *

#molecules C, N, O, Cl, H, H2, O2, OH, CO2, H2O

mol_file_prefix = "/home/wladerer/github/vaspy/resources/molecules"

c = molecule_from_file(f"{mol_file_prefix}/C.xyz")
co = molecule_from_file(f"{mol_file_prefix}/CO.xyz")
co2 = molecule_from_file(f"{mol_file_prefix}/CO2.xyz")
h2 = molecule_from_file(f"{mol_file_prefix}/H2.xyz")
h2o = molecule_from_file(f"{mol_file_prefix}/H2O.xyz")
oh = molecule_from_file(f"{mol_file_prefix}/OH.xyz")

#make the remaining molecules using pymatgen
cl = Molecule(["Cl"], [[0,0,0]])
n = Molecule(["N"], [[0,0,0]])
o = Molecule(["O"], [[0,0,0]])
h = Molecule(["H"], [[0,0,0]])

#create a list of all the molecules
molecules = [c, co, co2, h2, h2o, oh, cl, n, o, h]

