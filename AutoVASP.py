from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Union

import pandas as pd
from mp_api.client import MPRester
from pymatgen.analysis.adsorption import AdsorbateSiteFinder
from pymatgen.core.structure import Molecule, Structure
from pymatgen.core.surface import SlabGenerator
from pymatgen.io.vasp.inputs import Incar, Kpoints, Poscar, Potcar
from pymatgen.io.vasp.outputs import (BSVasprun, Chgcar, Eigenval, Outcar,
                                      Procar, Vasprun)
from pymatgen.symmetry.bandstructure import HighSymmKpath

job_types: dict = {
    "bulk_relaxation_low_prec": {"System": "AutoVASP Low Precision Bulk Relaxation", "PREC": "NORMAL", "ENCUT": "520", "ISTART": "0", "ICHARG": "2", "ISPIN": "1", "NELM": "60", "NELMIN": "2", "NELMDL": "10", "EDIFF": "1.0E-05", "LREAL": "Auto", "IALGO": "48", "VOSKOWN": "1", "ADDGRID": ".TRUE.", "EDIFFG": "-1.0E-04", "NSW": "25", "IBRION": "2", "ISIF": "3", "SIGMA": "0.10", "ISMEAR": "0"},
    "bulk_relaxation_med_prec": {"System": "AutoVASP Med. Precision Bulk Relaxation", "PREC": "Accurate", "ENCUT": "520", "ISTART": "0", "ICHARG": "2", "ISPIN": "1", "NELM": "60", "NELMIN": "2", "NELMDL": "10", "EDIFF": "1.0E-06", "LREAL": "Auto", "IALGO": "48", "VOSKOWN": "1", "ADDGRID": ".TRUE.", "EDIFFG": "-1.0E-05", "NSW": "25", "IBRION": "2", "ISIF": "3", "SIGMA": "0.10", "ISMEAR": "0"},
    "bulk_relaxation_high_prec": {"System": "AutoVASP High Precision Bulk Relaxation", "PREC": "Accurate", "ENCUT": "520", "ISTART": "0", "ICHARG": "2", "ISPIN": "1", "NELM": "60", "NELMIN": "3", "NELMDL": "10", "EDIFF": "1.0E-07", "LREAL": "Auto", "IALGO": "48", "VOSKOWN": "1", "ADDGRID": ".TRUE.", "EDIFFG": "-1.0E-06", "NSW": "25", "IBRION": "2", "ISIF": "3", "SIGMA": "0.10", "ISMEAR": "0"},
    "slab_relaxation_low_prec": {"System": "AutoVASP Low Precision Slab Relaxation", "PREC": "NORMAL", "ENCUT": "520", "ISTART": "0", "ICHARG": "2", "ISPIN": "1", "NELM": "60", "NELMIN": "2", "NELMDL": "10", "EDIFF": "1.0E-05", "LREAL": "Auto", "IALGO": "48", "VOSKOWN": "1", "ADDGRID": ".TRUE.", "EDIFFG": "-1.0E-04", "NSW": "25", "IBRION": "2", "ISIF": "2", "SIGMA": "0.10", "ISMEAR": "0"},
    "slab_relaxation_med_prec": {"System": "AutoVASP Med. Precision Slab Relaxation", "PREC": "Accurate", "ENCUT": "520", "ISTART": "0", "ICHARG": "2", "ISPIN": "1", "NELM": "60", "NELMIN": "2", "NELMDL": "10", "EDIFF": "1.0E-06", "LREAL": "Auto", "IALGO": "48", "VOSKOWN": "1", "ADDGRID": ".TRUE.", "EDIFFG": "-1.0E-05", "NSW": "25", "IBRION": "2", "ISIF": "2", "SIGMA": "0.10", "ISMEAR": "0"},
    "slab_relaxation_high_prec": {"System": "AutoVASP High Precision Slab Relaxation", "PREC": "Accurate", "ENCUT": "520", "ISTART": "0", "ICHARG": "2", "ISPIN": "1", "NELM": "60", "NELMIN": "3", "NELMDL": "10", "EDIFF": "1.0E-07", "LREAL": "Auto", "IALGO": "48", "VOSKOWN": "1", "ADDGRID": ".TRUE.", "EDIFFG": "-1.0E-06", "NSW": "25", "IBRION": "2", "ISIF": "2", "SIGMA": "0.10", "ISMEAR": "0"},
    "spin_orbit": {"SYSTEM": "Spin-Orbit Coupling Calculation", "LSORBIT": ".TRUE.", "GGA_COMPAT": ".FALSE.", "VOSKOWN": "1", "LMAXMIX": "4", "ISYM": "-1", "NBANDS": "set_bands_manually", "LORBIT": "11", "EDIFF":"1.06E-06"},
    "dos": {"System": "AutoVASP Density of States", "ISPIN": "1", "PREC": "Accurate", "NSW": "0", "ISMEAR": "-5", "ENCUT": "520", "NEDOS": "5000", "LORBIT": "11", "EMIN": "-10", "EMAX": "8"},
    "band": {"System": "AutoVASP Band Structure Calculation", "ICHARG": "11", "ENCUT": "520", "ISMEAR": "0", "SIGMA": "0.1", "LORBIT": "11"},
    "mBJ": {"SYSTEM": "AutoVASP generated MBJ", "METAGGA": "MBJ", "CMBJ": "1.2", "LASPH": ".TRUE.", "LWAVE": ".TRUE.", "LCHARG": ".TRUE.", "LELF": ".TRUE.", "LORBIT": "11", "LSORBIT": ".TRUE.", "ENCUT": "520", "EDIFF": "1E-7", "LREAL": ".False.", "ISTART": "0", "ISYM": "-1", "NELMIN": "8"},
    "bdcd": {"SYSTEM": "Band Decomposed Charge Densiy", "LPARD": ".TRUE."}
}


def structure_from_mpi_code(mpcode: str, api_key: str) -> Structure:
    '''
    Creates a pymatgen structure from a code
    '''
    if not mpcode.startswith("mp-"):
        mpcode = "mp-"+mpcode

    with MPRester(api_key) as mpr:
        structure = mpr.get_structure_by_material_id(mpcode, conventional_unit_cell=True)

    return structure


def structure_from_file(filename: str) -> Structure:
    '''
    Creates a pymatgen structure from a file
    '''
    structure = Structure.from_file(filename, sort=True, primitive=False)

    return structure


def molecule_from_file(filename: str) -> Molecule:
    '''
    Creates a pymatgen molecule from a file
    '''
    molecule = Molecule.from_file(filename)

    return molecule


def addAdsorbate(structure: Structure, adsorbate: Molecule, min_z: float = 5.0, coverage: list[int] = [1, 1, 1]) -> list[Structure]:
    '''
    Finds all adsorption sites on a structure and adsorbs the adsorbate at each site. Returns a list of adsorbed structures.
    '''

    asf = AdsorbateSiteFinder(structure)
    ads_structs = asf.generate_adsorption_structures(adsorbate, repeat=coverage, find_args={"distance": 1.6})  # edit later

    for ads_struct in ads_structs:
        for site in ads_struct:
            if site.z < min_z:
                site.properties["selective_dynamics"] = [False, False, False]
            else:
                site.properties["selective_dynamics"] = [True, True, True]

    return ads_structs


def slabs_from_structure(structure: Structure, miller_index: list[int], min_slab_size: float = 15.0, min_vacuum_size: float = 15.0, use_in_unit_planes: bool = False, ensure_symmetric_slabs: bool = True, min_z: int = 5) -> list[Structure]:
    '''
    Function to generate slabs from a structure
    '''

    slab_generator = SlabGenerator(initial_structure=structure, miller_index=miller_index, min_slab_size=min_slab_size,
                                   min_vacuum_size=min_vacuum_size, primitive=False, in_unit_planes=use_in_unit_planes)
    slabs = slab_generator.get_slabs()
    if ensure_symmetric_slabs:
        slabs = [slab for slab in slabs if slab.is_symmetric()]

    if len(slabs) == 0:
        raise ValueError("No slabs generated, consider changing the slab parameters or change ensure_symmetric_slabs to False")

    print(f"Generated {len(slabs)} slabs")

    # freeze the bottom layer
    for slab in slabs:
        slab = freeze_structure(slab, min_z)

    return slabs


def extend_structure(structure, x_repeat: int = 1, y_repeat: int = 1 , z_repeat: int = 1) -> Structure:
    '''
    Extends a structure in the x, y, and z directions
    '''
    structure.make_supercell([x_repeat, y_repeat, z_repeat])

    return structure


def freeze_structure(structure: Structure, min_z: float) -> Structure:
    '''
    Freezes the bottom layer of a structure
    '''
    for site in structure:
        if site.z < min_z:
            site.properties["selective_dynamics"] = [False, False, False]
        else:
            site.properties["selective_dynamics"] = [True, True, True]

    return structure


def structure_to_dataframe(structure: Structure) -> pd.DataFrame:
    '''
    Converts a pymatgen structure to a pandas dataframe
    '''
    formula = structure.composition.reduced_formula
    a = structure.lattice.a
    b = structure.lattice.b
    c = structure.lattice.c
    alpha = structure.lattice.alpha
    beta = structure.lattice.beta
    gamma = structure.lattice.gamma
    volume = structure.volume
    num_species = len(structure.composition.elements)
    num_sites = len(structure.sites)
    # check if the structure has been frozen
    if "selective_dynamics" in structure.sites[0].properties:
        frozen = True
    else:
        frozen = False

    k_x, k_y, k_z = recommended_kpoints(structure)["kpoints"]

    data = {"formula": formula, "a": a, "b": b, "c": c, "alpha": alpha, "beta": beta, "gamma": gamma, "volume": volume,
            "num_species": num_species, "num_sites": num_sites, "frozen": frozen, "k_x": k_x, "k_y": k_y, "k_z": k_z}
    df = pd.DataFrame(data, index=[0])

    return df


def recommended_kpoints(structure: Structure) -> dict:
    '''
    Returns recommended kpoints for a structure
    '''
    k_x, k_y, k_z = 50/structure.lattice.a, 50/structure.lattice.b, 50/structure.lattice.c
    kpoints = {"kpoints": [k_x, k_y, k_z]}
    return kpoints


def make_kpoints(structure: Structure, scale: list[float] = [50, 50, 50], force_gamma: bool = True) -> Kpoints:
    '''
    Creates a pymatgen Kpoints object, scales the kpoints by length of the lattice vectors
    '''

    kpoints = Kpoints.automatic_density_by_lengths(structure, scale, force_gamma=force_gamma)
    return kpoints


def make_poscar(structure: Structure, sort: bool = True) -> Poscar:
    '''
    Creates a pymatgen Poscar object
    '''
    poscar = Poscar(structure, sort_structure=sort)

    return poscar


def make_potcar(structure: Structure) -> Potcar:
    '''
    Creates a pymatgen Potcar object (default is PBE)
    '''
    # return elements as a list of strings
    elements = [str(element) for element in structure.composition.elements]
    recommended_potential_dict = {"Bi": "Bi_d", "Ba": "Ba_sv", "Ca": "Ca_sv", "Li": "Li_sv", "K": "K_sv", "Cr": "Cr_pv", "Cu": "Cu_pv", "Cs": "Cs_sv", "Hf": "Hf_pv", "Mn": "Mn_pv", "Mo": "Mo_pv",
                                  "Nb": "Nb_pv", "Ni": "Ni_pv", "Os": "Os_pv", "Pd": "Pd_pv", "Rb": "Rb_sv", "Re": "Re_pv", "Rh": "Rh_pv", "Ru": "Ru_pv", "Ta": "Ta_pv", "Tc": "Tc_pv", "Ti": "Ti_pv", "V": "V_pv", "W": "W_pv"}

    # replace elements with the correct potential
    for i, element in enumerate(elements):
        if element in recommended_potential_dict:
            elements[i] = recommended_potential_dict[element]

    potcar = Potcar(elements)

    return potcar


def make_incar(parameter_dictionary: dict) -> Incar:
    '''
    Makes an Incar object from a structure
    '''
    incar = Incar(parameter_dictionary)
    return incar


def make_kpath(structure: Structure, divisions: int = 40) -> Kpoints:
    '''
    Makes a linemode Kpoints object from a structure
    '''
    kpath = HighSymmKpath(structure)
    kpoints = Kpoints.automatic_linemode(divisions, kpath)
    kpoints.write_file("KPATH.av")

    return kpoints


def check_for_valid_tags(dict):
    '''
    Checks to see if the dictionary has valid tags
    '''
    # tags file is a text file with all the valid tags found in the resources folder
    with open("resources/tags.txt", "r") as f:
        valid_tags = f.read().splitlines()
    # check to see if the dictionary has valid tags
    # print all invalid tags
    for key in dict:
        if key not in valid_tags:
            print(key, "is not a valid tag")
            return False
        else:
            return True


def incar_dict_from_incar_file(file: str) -> dict:
    '''
    Finds all tags in a file and returns a dictionary of the tags and their values
    '''

    # read the file
    with open(file, "r") as f:
        lines = f.readlines()

    # remove text after # and remove newlines
    lines = [line.split("#")[0].strip() for line in lines]

    # find all the tags and their values
    incar_dict = {}
    for line in lines:
        if "=" in line:
            tag, value = line.split("=")
            incar_dict[tag.strip()] = value.strip()

    return incar_dict


def incar_dict_from_json(file: str) -> dict:
    '''
    Converts json file to a dictionary
    '''

    with open(file, "r") as f:
        incar_dict = json.load(f)

    # verify that the dictionary has valid tags
    if check_for_valid_tags(incar_dict) == False:
        print("WARNING: INCAR DICTIONARY HAS INVALID TAGS")
        print("WARNING: A dictionary is still returned, but it may not be valid")

    return incar_dict


def update_incar_dict(incar_dict: dict, update_dict: dict) -> dict:
    '''
    Updates the incar dictionary with the tags from the tags dictionary
    '''

    for key in update_dict:
        incar_dict[key] = update_dict[key]

    return incar_dict


def create_readme(structure: Structure, directory: str):

    with open(directory + "/README.txt", "w") as f:
        f.write("This directory contains the input files for a VASP calculation created by AutoVASP\n")
        f.write(f"The date and time of creation is {datetime.now()} \n")
        f.write(f"The structure is {structure.composition.reduced_formula}\n")
        f.write(f"The space group is {structure.get_space_group_info()[0]}\n")
        f.write(f"The lattice parameters are {structure.lattice.abc} and angles are {structure.lattice.angles}\n")


def compare_structures(structure1: Structure, structure2: Structure) -> dict:
    '''
    Compares two structures and returns a dictionary containing the diffrerences
    '''
    # compare the lattice parameters
    a1, b1, c1 = structure1.lattice.abc
    a2, b2, c2 = structure2.lattice.abc
    alpha1, beta1, gamma1 = structure1.lattice.angles
    alpha2, beta2, gamma2 = structure2.lattice.angles
    d_a, d_b, d_c, d_alpha, d_beta, d_gamma = a2 - a1, b2 - b1, c2 - c1, alpha2 - alpha1, beta2 - beta1, gamma2 - gamma1
    # compare volume
    dV = structure2.volume - structure1.volume

    # add the differences to a dictionary
    results = {"d_a": d_a, "d_b": d_b, "d_c": d_c, "d_alpha": d_alpha, "d_beta": d_beta, "d_gamma": d_gamma, "dV": dV}

    return results


def init_vasp_input_files(structure: Structure) -> dict:
    '''
    Creates the input files for a VASP calculation from a structure
    Returns a dictionary containing the input files
    '''
    input_files_dict = {"poscar": make_poscar(structure), "potcar": make_potcar(
        structure), "kpoints": make_kpoints(structure), "kpath": make_kpath(structure)}

    return input_files_dict


class vaspInput:
    '''
    A class that makes, updates, and writes VASP input files
    '''

    def __init__(self, structure: Structure, parameter_dictionary: dict) -> None:
        self.structure: Structure = structure
        self.parameter_dictionary: dict = parameter_dictionary
        self.poscar: Poscar
        self.potcar: Potcar
        self.incar: Incar
        self.kpoints: Kpoints
        self.kpath: Union[Kpoints, None]
        self.data = Union[pd.DataFrame, None]
        self.initialize_files()

    def initialize_files(self):
        '''
        Initializes the input files
        '''
        self.poscar = make_poscar(self.structure)
        self.potcar = make_potcar(self.structure)
        self.incar = make_incar(self.parameter_dictionary)
        self.kpoints = make_kpoints(self.structure)
        self.kpath = make_kpath(self.structure)

    def make_input_files(self, updated_parameter_dictionary: Union[dict, None] = None) -> dict:
        '''
        Makes input files for VASP
        Allows user to pass in a dictionary of tags and values to update the INCAR
        '''

        if updated_parameter_dictionary != None:
            incar = make_incar(updated_parameter_dictionary)
        else:
            incar = make_incar(self.parameter_dictionary)

        structure = self.structure
        input_files = init_vasp_input_files(structure)
        input_files["incar"] = incar

        return input_files

    # make a class method that creates a vasp input object from a directory
    @classmethod
    def from_directory(cls, directory: str) -> vaspInput:
        '''
        Creates a vaspInput object from a directory
        '''
        parameter_dictionary = Incar.from_file(directory + "/INCAR").as_dict()
        structure = Poscar.from_file(directory + "/POSCAR").structure
        vasp_input = cls(structure, parameter_dictionary)

        return vasp_input

    def as_dataframe(self) -> pd.DataFrame:
        '''
        Returns a dataframe of the input files
        '''
        formula = self.structure.composition.reduced_formula
        a, b, c = self.structure.lattice.abc
        alpha, beta, gamma = self.structure.lattice.angles
        volume = self.structure.volume
        num_species = len(self.structure.composition.elements)
        sym_symbol, intl_number = self.structure.get_space_group_info()
        k_x, k_y, k_z = self.kpoints.kpts[0]  # type: ignore
        n_kpoints = self.kpoints.num_kpts

        data = {"formula": formula, "a": a, "b": b, "c": c, "alpha": alpha, "beta": beta, "gamma": gamma, "volume": volume,
                "num_species": num_species, "sym_symbol": sym_symbol, "intl_number": intl_number, "k_x": k_x, "k_y": k_y, "k_z": k_z, "n_kpoints": n_kpoints}
        df = pd.DataFrame(data, index=[0])

        return df

    def write_input_files(self, directory: str, readme: bool = False) -> None:
        '''
        Writes input files to a directory
        Optionally writes a README.txt file and initial_parameters.csv file
        '''

        # make the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.poscar.write_file(directory + "/POSCAR")
        self.incar.write_file(directory + "/INCAR")
        self.potcar.write_file(directory + "/POTCAR")
        self.kpoints.write_file(directory + "/KPOINTS")
        if self.kpath is not None:
            self.kpath.write_file(directory + "/KPATH")

        if readme:
            create_readme(self.structure, directory)
            self.as_dataframe().to_csv(directory + "/initial_parameters.csv")

        return None


class vaspOutput:
    '''
    A class that reads VASP output files
    '''

    def __init__(self, directory: str) -> None:
        self.directory = directory

        # create a vaspInput object
        self.incar = Incar.from_file(directory + "/INCAR")
        self.poscar = Poscar.from_file(directory + "/POSCAR")
        self.potcar = Potcar.from_file(directory + "/POTCAR")
        self.kpoints = Kpoints.from_file(directory + "/KPOINTS")
        self.kpath = Kpoints.from_file(directory + "/KPATH")
        self.initial_structure = self.poscar.structure
        self.final_structure = Poscar.from_file(directory + "/CONTCAR").structure
        self.outcar: Outcar
        self.chgcar: Chgcar
        self.eigenval: Eigenval
        self.vasprun: Vasprun
        self.procar: Procar
        self.bsvasprun: BSVasprun
        self.doscar: str  # pymatgen does not have a Doscar class
        self.data = None

    def from_directory(self, directory: str) -> list:

        outcar = Outcar(directory + "/OUTCAR")
        chgcar = Chgcar.from_file(directory + "/CHGCAR")
        eigenval = Eigenval(directory + "/EIGENVAL")
        vasprun = Vasprun(directory + "/vasprun.xml")
        procar = Procar(directory + "/PROCAR")
        bsvasprun = BSVasprun(directory + "/vasprun.xml")
        doscar = directory + "/DOSCAR"

        # update vaspOutput object
        self.outcar = outcar
        self.chgcar = chgcar
        self.eigenval = eigenval
        self.vasprun = vasprun
        self.procar = procar
        self.bsvasprun = bsvasprun
        self.doscar = doscar

        return [outcar, chgcar, eigenval, vasprun, procar, bsvasprun, doscar]

    def as_dataframe(self) -> pd.DataFrame:
        '''
        Creates a pandas dataframe of the output files
        '''
        formula = self.vasprun.final_structure.composition.reduced_formula
        a, b, c = self.vasprun.final_structure.lattice.abc
        alpha, beta, gamma = self.vasprun.final_structure.lattice.angles
        volume = self.vasprun.final_structure.volume
        num_species = len(self.vasprun.final_structure.composition.elements)
        sym_symbol, intl_number = self.vasprun.final_structure.get_space_group_info()
        k_x, k_y, k_z = self.vasprun.kpoints.kpts
        n_kpoints = self.vasprun.kpoints.num_kpts
        energy = self.vasprun.final_energy
        energy_per_atom = self.vasprun.final_energy / self.vasprun.final_structure.num_sites

        data = {"formula": formula, "a": a, "b": b, "c": c, "alpha": alpha, "beta": beta, "gamma": gamma, "volume": volume, "num_species": num_species,
                "sym_symbol": sym_symbol, "intl_number": intl_number, "k_x": k_x, "k_y": k_y, "k_z": k_z, "n_kpoints": n_kpoints, "energy": energy, "energy_per_atom": energy_per_atom}
        df = pd.DataFrame(data, index=[0])

        return df

    def structure_changes(self) -> dict:
        '''
        Returns a dictionary of various structual changes
        General format is final - initial 
        '''

        return compare_structures(self.initial_structure, self.final_structure)

    def to_csv(self):
        '''
        Writes the output files to a csv file
        '''

        df = self.as_dataframe()
        df = df.join(pd.DataFrame(self.structure_changes(), index=[0]))
        df.to_csv(self.directory + "/output.csv")

        return None

    def prepare_dos_directory(self, lobster: bool = False):
        '''
        Creates a directory that will be used for a DOS calculation
        '''

        # create the directory
        dos_directory = self.directory + "/DOS"
        # if lobster , add lobster to the directory name
        if lobster:
            dos_directory += "_lobster"

        if not os.path.exists(dos_directory):
            os.makedirs(dos_directory)

        # copy CONTAR to DOS/POSCAR
        os.system("cp " + self.directory + "/CONTCAR " + dos_directory + "/POSCAR")

        # copy the vasprun.xml file using os.system
        files_to_copy = ["vasprun.xml", "KPOINTS", "CHGCAR", "WAVECAR", "POTCAR"]
        for file in files_to_copy:
            os.system("cp " + self.directory + "/" + file + " " + dos_directory + "/" + file)

        return None

    def prepare_band_directory(self) -> None:
        '''
        Prepares a directory for a band structure calculation
        '''

        # create the directory

        band_directory = self.directory + "/BAND"
        if not os.path.exists(band_directory):
            os.makedirs(band_directory)

        # copy CONTAR to BAND/POSCAR
        os.system("cp " + self.directory + "/CONTCAR " + band_directory + "/POSCAR")

        # copy the vasprun.xml file using os.system
        files_to_copy = ["vasprun.xml", "KPOINTS", "CHGCAR", "WAVECAR", "POTCAR"]
        for file in files_to_copy:
            os.system("cp " + self.directory + "/" + file + " " + band_directory + "/" + file)

        return None


def make_directory_name(structure: Structure, incar_type: str) -> str:

    # get reduced formula and remove non-alphanumeric characters
    formula = structure.composition.reduced_formula
    formula = re.sub('[^A-Za-z0-9]+', '', formula)
    directory_name = f"{formula}_{incar_type}"

    return directory_name


def write_job_files(structure: Structure, incar_type: str, save_dir: str = "./", readme: bool = False) -> None:
    '''
    Creates a directory and populates it with input files for a VASP calculation
    '''

    param_dict = job_types[incar_type]
    input = vaspInput(structure, param_dict)
    input.write_input_files(save_dir, readme=readme)

    return None


def create_job_array(structure_list: list[Structure]) -> pd.DataFrame:
    '''
    Creates a pandas dataframe comparing the input parameters of a list of structures
    '''

    input_list = [vaspInput(structure, job_types["bulk_relaxation_med_prec"]) for structure in structure_list]
    df = pd.concat([input.as_dataframe() for input in input_list], ignore_index=True)

    return df

