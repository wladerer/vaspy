#import Moleculs from pymatgen
from pymatgen.core import Molecule
from pymatgen.io.xyz import XYZ

def make_vacuum(file, vacuum: float):
   '''
   Uses get_boxed_structure to make a vacuum around the molecule
   Saves as POSCAR
   '''
   mol = Molecule.from_file(file)
   #get reduced formula
   formula = mol.composition
   mol_boxed = mol.get_boxed_structure(vacuum, vacuum, vacuum)
   #get reduced formula
   mol_boxed.to(fmt='poscar', filename=f"{formula}.poscar")
   
#convert all .xyz files to .poscar   
import os
for file in os.listdir():
   if file.endswith(".xyz"):
      make_vacuum(file, 15)
   
#remove any spaces in the file names
import os
for file in os.listdir():
   os.rename(file, file.replace(" ", ""))

#remove the number 1 from file names
import os
for file in os.listdir():
   os.rename(file, file.replace("1", ""))

   
