import os
import subprocess as sp
import numpy as np
from ase.build import sort
from ase.io import read as ase_read
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pprint import pprint

def write_insod_lines(title, atoms, cell_params, nspecies, symbols, len_symbols, coords, supercell, target_idx, subs, subtype, filer = ("11 0"), ishell = ("0 1"), newshell = ("0 0") ):
    atoms = sort(atoms)
    lines = []
    lines.append("#Title")
    lines.append(title)
    lines.append("")
    lines.append("# a,b,c,alpha,beta,gamma")
    lines.append(cell_params)
    lines.append("")
    lines.append("# nsp: Number of species in the parent structure")
    lines.append(len_symbols)
    lines.append("")
    lines.append("# symbol(1:nsp): Atom symbols")
    lines.append(symbols)
    lines.append("")
    lines.append("# natsp0(1:nsp): Number of atoms for each species in the assymetric unit")
    lines.append(nspecies)
    lines.append("")
    lines.append("# coords0(1:nat0,1:3): Coordinates of each atom (one line per atom)")
    for coord in coords:
        lines.append(coord)
    lines.append("")
    lines.append("# na,nb,nc (supercell definition)")
    lines.append(supercell)
    lines.append("")
    lines.append("# sptarget: Species to be substituted")
    lines.append(target_idx)
    lines.append("")
    lines.append("# nsubs: Number of substitutions in the supercell")
    lines.append(subs)
    lines.append("")
    lines.append("# newsymbol(1:2): Symbol of atom to be inserted in the selected position, ")
    lines.append("# symbol to be inserted in the rest of the positions for the same species.")
    lines.append(subtype)
    lines.append("")
    lines.append("# FILER, MAPPER")
    lines.append("# FILER:   0 (no calc files generated), 1 (GULP), 2 (METADISE), 11 (VASP)")
    lines.append("# MAPPER:  0 (no mapping, use currect structure), >0 (map to structure in MAPTO file)")
    lines.append("# (each position in old structure is mapped to MAPPER positions in new structure)")
    lines.append(filer)
    lines.append("")
    lines.append("# If FILER=1 then: ")
    lines.append("# ishell(1:nsp) 0 core only / 1 core and shell (for the species listed in symbol(1:nsp)) ")
    lines.append(ishell)
    lines.append("# newshell(1:2) 0 core only / 1 core and shell (for the species listed in newsymbol(1:2))")
    lines.append(newshell)


    with open("INSOD", "w") as f:
        for line in lines:
            f.write(str(line))
            f.write("\n")
    return 0

def write_sgo(name, number, ops):
    # Check for existing SGO?
    with open("SGO", "w") as f:
        f.write(f"Space group {number} for {name}\n")
        for idx, op in enumerate(ops, 1):
            f.write(f"{idx}\n")
            rotm = op.rotation_matrix
            tranv = op.translation_vector
            for jdx, elem in enumerate(rotm):
                f.write(f"  {elem[0]}  {elem[1]}  {elem[2]}   {tranv[jdx]}\n")
        f.write("0\n")

        





