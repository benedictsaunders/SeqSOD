from ase.io import read as ase_read, write as ase_write
from pymatgen.core.periodic_table import Element
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
import concurrent.futures
import argparse as ap
from pyfiglet import Figlet
from ase.build import make_supercell, sort as ase_sort
from write_files import write_insod_lines, write_sgo
from utils import *
from itertools import repeat
import subprocess as sp
import shutil
from tqdm import tqdm

IGNORE_SPECIES = ["O", "S", "Cl", "F", "H", "C", "Si", "Br", "I"]

def get_input_params(atoms, target, dopant, supercell):

    param_string = " ".join(["{:.3f}".format(p) for p in atoms.cell.cellpar()])
    # Not using set here because we want to preserve the order
    usymbols = []
    counts = []
    symbols = list(atoms.symbols)
    for s in symbols:
        if s not in usymbols:
            usymbols.append(s)
    for us in usymbols:
        counts.append(str(symbols.count(us)))
    scaled_positions_strs = []
    for position in atoms.get_scaled_positions():
        position = " ".join(["{:.3f}".format(p) for p in position])
        scaled_positions_strs.append(position)

    cnt_usymbols = str(len(usymbols))
    counts = " ".join(counts)
    usymbols = " ".join(usymbols)
    supercell = " ".join(supercell)
    target_idx = usymbols.index(target) + 1 # Fortran starts at 1 and needs to get in the bin

    replacement = f"{dopant} {target}"

    return param_string, cnt_usymbols, usymbols, counts, scaled_positions_strs, supercell, target_idx, replacement

def number_target_sites(atoms, target):
    symbols = atoms.get_chemical_symbols()
    return symbols.count(target)

def symmops(atoms):
    struct = AseAtomsAdaptor.get_structure(atoms)
    sga = SpacegroupAnalyzer(struct)
    sg_number = sga.get_space_group_number()
    sg_operations = sga.get_space_group_operations()
    return sg_number, sg_operations

def sod_task(it, atoms, params):
    """
    THIS IS THE MAIN EVENT!
    """
    cellpar, cnt_uqsym, uqsym, counts, frac_pos, scell, tidx, rep = params
    idx = it.split("_")[-1]
    with cd(str(it)):
        write_insod_lines(f"ID {it   }", atoms, cellpar, counts, uqsym, cnt_uqsym, frac_pos, scell, tidx, it, rep)
        shutil.copy2("../SGO", ".")

        print(f" > Running SOD for permutation {idx}.")
        sod_log = open("SODLOG", "w")
        sp.call(["sod_comb.sh"], stdout=sod_log, stderr=sod_log)
        print(f" > Finished SOD for permutation {idx}.")

    return it


def generate_endpoints(atoms, supercell, target, dopant):
    print(" > Generating endpoints.")
    P = [
        [int(supercell[0]), 0, 0],
        [0, int(supercell[1]), 0],
        [0, 0, int(supercell[2])],
    ]
    endpoints = []
    atoms = ase_sort(make_supercell(atoms, P))
    symbols = atoms.get_chemical_symbols()
    for sub in (target, dopant):
        new_symbols = [sub if s not in IGNORE_SPECIES else s for s in symbols]
        atoms.set_chemical_symbols(new_symbols)
        stoms = ase_sort(atoms)
        with cd("endpoints/CALCS"):
            formula = atoms.get_chemical_formula(mode='metal', empirical=True)
            ase_write(f"endpoint_{formula}.vasp", atoms)


def collect_structs(sequence, name = "", ext = "vasp"):
    if name != "":
        name = f"{name}_"
    os.mkdir("ALL_STRUCTS")
    for member in sequence:
        with cd(str(member) + "/CALCS"):
            move_and_rename(f"*.{ext}", prefix = name + str(member) + "_", pbar_desc = f"Handling {member}")
    

if __name__ == "__main__":

    # First and foremost we have to make it look profesh, otherwise what's the point?
    cli_header()

    parser = ap.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Geometry input file, readable by ASE.", metavar="<file>")
    parser.add_argument("-d", "--dopants", required=True, metavar="<symbol>")
    parser.add_argument("-t", "--target", required=True, metavar="<symbol>")
    parser.add_argument("-r", "--supercell", default=("1", "1", "1"), nargs=3, help="Create a supercell of the input in X Y Z.", metavar=("<x", "y", "z>"))
    parser.add_argument("-n", "--name", metavar="<name>", default = "", help="Output prefix, defaults to ''.")

    parser.add_argument("-c", "--convert", action="store_true", help="Convert all metal/non chalcogen sites to a target.")
    parser.add_argument("-f", "--force", action="store_true", help="Force overwrite of directories, overwriting previous runs.")
    parser.add_argument("--ignoredopant", action="store_true", help="Ignore any existing dopants if --convert is used.")
    parser.add_argument("--override", action="store_true")
    args = parser.parse_args()

    atoms = ase_read(args.input)
    name = args.input
    target, dopants, supercell, to_target, ignore_dopant, force_ow = args.target, args.dopants, args.supercell, args.convert, args.ignoredopant, args.force
    override, name = args.override, args.name

if not override:
    handle_input(supercell)
handle_overwrite(force = force_ow)

if to_target:
    species = set(atoms.get_chemical_symbols())
    to_ignore = IGNORE_SPECIES
    if ignore_dopant:
        to_ignore.append(dopants)
    struct = AseAtomsAdaptor.get_structure(atoms)
    for element in list(species):
        if element not in to_ignore:
            struct.replace_species(
                dict({Element(element):Element(target)})
            )
    print(struct)
    atoms = AseAtomsAdaptor.get_atoms(struct)

atoms = ase_sort(atoms)
params = get_input_params(atoms, target, dopants, supercell)
mult = [int(i) for i in supercell]
its = number_target_sites(atoms, target) * mult[0] * mult[1] * mult[2]

write_sgo(name, *symmops(atoms))
endpoints = generate_endpoints(atoms, supercell, dopants, target)
dirs = [f"sqsd_{i}" for i in range(1, its)]
with concurrent.futures.ProcessPoolExecutor(max_workers=its) as executor:
    r = executor.map(sod_task, dirs, repeat(atoms), repeat(params))
sequence = list(r) + ["endpoints"]
collect_structs(sequence=sequence, name = name)






    

    


    
