# SeqSOD

A sequential approach to Grau-Crespo's SOD (Site Occupancy Disorder) code.

## Motivation and Philosophy

Alone, SOD is able to produce all symmetric inequivalent permutations of a substitution in a given material. However, when it comes to exploring phase space, using single stoichiometries becomes inefficient. SeqSOD, or Sequential SOD iterates over specified target sites, and runs SOD for each combination in parallel. 

SOD does already have a method to approximate the energies for a new composition by extrapolating from previous calculations, butt his does not work well for phase spaces with high convexity.

### Why are SOD runs duplicated for the inverse of the site occupations?

Structures in SeqSOD are handled with ASE. While it would make sense intially to cut the SOD runs in half and replace the atoms individually, it is actually computationally cheaper to duplicate the SOD runs, particularly for systems with highly asymmetric permutations. Perhaps it would work if running this serially though. But why would you do that in today's day and age where even your mobile phone has multiple cores.