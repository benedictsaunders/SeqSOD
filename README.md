# SeqSOD

A sequential approach to Grau-Crespo's SOD (Site Occupancy Disorder) code.

## Motivation and Philosophy

Alone, SOD is able to produce all symmetric inequivalent permutations of a substitution in a given material. However, when it comes to exploring phase space, using single stoichiometries becomes inefficient. SeqSOD, or Sequential SOD iterates over specified target sites, and runs SOD for each combination in parallel. 

SOD does already have a method to approximate the energies for a new composition by extrapolating from previous calculations, butt his does not work well for phase spaces with high convexity.
