import os

import pandas as pd
from pymatgen.core.structure import Molecule, Structure

from AutoVASP import *

api_key = "aOGNgkSFnNArzpnQT5ff8RIErnX1TNIz"

def test_AutoVASP():
    # Test the AutoVASP class
    # Path: tests/test_AutoVASP.py
    test_structure: Structure = Structure.from_file("POSCAR")
    test_adsorbate: Molecule = Molecule.from_file("H2O.xyz")
    test_param_dict: dict = {"SYSTEM": "test", "ISTART":0, "ENCUT": 500, "EDIFF": 1e-6, "LWAVE":".TRUE.", "LELF":".TRUE."}
    dir = "write_input_files_test/"
    
    # #test if structure_from_mpi_code returns a structure
    # assert isinstance(structure_from_mpi_code('mp-1234', api_key), Structure)
    # #test if structure_from_mpi_code returns a structure even if it is missing the mp- prefix
    # assert isinstance(structure_from_mpi_code('1234', api_key), Structure)

    #test if structure_from_file returns a structure object
    assert isinstance(structure_from_file('POSCAR'), Structure)

    #test if molecule_from_file returns a Molecule object
    assert isinstance(molecule_from_file('H2O.xyz'), Molecule)

    # test if addAdsorbate returns a list of structures
    adsorbate_list = addAdsorbate(test_structure, test_adsorbate)
    assert isinstance(adsorbate_list, list)
    assert isinstance(adsorbate_list[0], Structure)


    #test if slabs_from_structure returns a list of structures
    assert isinstance(slabs_from_structure(test_structure, [0,0,1]), list)

    #test if structure_to_dataframe returns a pandas dataframe without empty columns
    assert isinstance(structure_to_dataframe(test_structure), pd.DataFrame)
    assert len(structure_to_dataframe(test_structure).columns) > 0

    #test if vaspInput class make_input_files returns a list
    assert isinstance(vaspInput(test_structure, test_param_dict).make_input_files(), dict)
    

    #test if vaspInput class write_input_files produces the correct number of files

    vaspInput(test_structure, test_param_dict).write_input_files(dir)
    assert len(os.listdir(dir)) == 5

    #test if vaspInput from_directory returns a vaspInput object
    assert isinstance(vaspInput.from_directory(directory=dir), vaspInput)

    #test if vaspInput as_dataframe returns a pandas dataframe without empty columns    
    assert isinstance(vaspInput(test_structure,test_param_dict).as_dataframe(), pd.DataFrame)
    assert len(vaspInput(test_structure,test_param_dict).as_dataframe().columns) > 0


if __name__ == "__main__":
    test_AutoVASP()
    os.system("rm -r write_input_files_test")
    os.system("rm KPATH.av")


