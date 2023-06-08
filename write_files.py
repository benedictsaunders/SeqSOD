import os
import subprocess as sp
import numpy as np
from ase.io import read as ase_read
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

def write_insod_lines(title, atoms, cell_params, nspecies, symbols, coords, supercell, target_idx, subs, subtype, filer = ("11 0"), ishell = ("0 1"), newshell = ("0 0") ):
    atoms = atoms.sort()
    lines = []
    lines.append("#Title")
    lines.append(title)
    lines.append()
    lines.append("# a,b,c,alpha,beta,gamma")
    lines.append(cell_params)
    lines.append()
    lines.append("# symbol(1:nsp): Atom symbols")
    lines.append(symbols)
    lines.append()
    lines.append("# natsp0(1:nsp): Number of atoms for each species in the assymetric unit")
    lines.append(nspecies)
    lines.append()
    lines.append("# coords0(1:nat0,1:3): Coordinates of each atom (one line per atom)")
    for coord in coords:
        lines.append(coord)
    lines.append()
    lines.append("# na,nb,nc (supercell definition)")
    lines.append(supercell)
    lines.append()
    lines.append("# sptarget: Species to be substituted")
    lines.append(target_idx)
    lines.append()
    lines.append("# nsubs: Number of substitutions in the supercell")
    lines.append(subs)
    lines.append()
    lines.append("# newsymbol(1:2): Symbol of atom to be inserted in the selected position, ")
    lines.append("# symbol to be inserted in the rest of the positions for the same species.")
    lines.append(subtype)
    lines.append()
    lines.append(filer)
    lines.append(ishell)
    lines.append(newshell)

    return 0

def write_sgo(atoms):
    if os.path.isfile("SGO"):
        with open("SGO", "r") as f:
            line = f.readline()
        sgo_file = int(line.split()[2])
        os.system("rm SGO")
    struct = ASEAtomsAdaptor.get_structure(atoms)
    sga = SpacegroupAnalyzer(struct)
    sg_number = sga.get_space_group_number()
    sg_operations = sga.get_space_group_operations()

