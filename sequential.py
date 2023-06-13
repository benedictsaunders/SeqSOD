from ase.io import read as ase_read
from pymatgen.core.periodic_table import Element
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
import concurrent.futures
import argparse as ap
from ase.build import sort as ase_sort
from write_files import write_insod_lines, write_sgo
from utils import *
from itertools import repeat
import subprocess as sp
import shutil
from tqdm import tqdm

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
    with cd(str(it)):
        write_insod_lines(f"Permutation - {it   }", atoms, cellpar, counts, uqsym, cnt_uqsym, frac_pos, scell, tidx, it, rep)
        shutil.copy2("../SGO", ".")

        print(f" > Running SOD for permutation {it}.")
        sod_log = open("SODLOG", "w")
        sp.call(["sod_comb.sh"], stdout=sod_log, stderr=sod_log)
        print(f" > Finished SOD for permutation {it}.")

      
    return it

def collect_structs(sequence, ext = "vasp"):
    os.mkdir("ALL_STRUCTS")
    for member in sequence:
        with cd(str(member) + "/CALCS"):
            prepend_filenames(f"*.{ext}")
        
        p = sp.Popen(["cp", f"{member}/CALCS/*.{ext}", "ALL_STRUCTS"])
        p.wait()

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="A sequential approach to using SOD")

    parser.add_argument("-i", "--input", required=True, help="Geometry input file, readable by ASE.")
    parser.add_argument("-d", "--dopants", required=True)
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-r", "--supercell", default=("1", "1", "1"), nargs=3, help="Create a supercell of the input in X Y Z.")
    parser.add_argument("-c", "--convert", action="store_true", help="Convert all metal/non chalcogen sites to a target.")
    parser.add_argument("--ignoredopant", action="store_true", help="Ignore any existing dopants if --convert is used.")

    args = parser.parse_args()

    atoms = ase_read(args.input)
    name = args.input
    target, dopants, supercell, to_target, ignore_dopant = args.target, args.dopants, args.supercell, args.convert, args.ignoredopant

if to_target:
    species = set(atoms.get_chemical_symbols())
    to_ignore = ["O", "S", "Cl", "F", "H", "C", "Si", "Br", "I"]
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

with concurrent.futures.ProcessPoolExecutor(max_workers=its) as executor:
    r = executor.map(sod_task, range(1, its), repeat(atoms), repeat(params))
sequence = list(r)
collect_structs(sequence=sequence)






    

    


    
